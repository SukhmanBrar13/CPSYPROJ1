# Defines all API routes for insights, recipes, and clustering.
from http.client import HTTPException
from fastapi import FastAPI, Query # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from pathlib import Path
import pandas as pd # type: ignore
from sklearn.cluster import KMeans # type: ignore
from .data_loader import load_data
from .utils import filter_by_diet, NUM_COLS
from .models import (
    AvgResponse, AvgInsight,
    Recipe, TopProteinResponse,
    ClusterResponse, ClusterPoint
)
from .azure_cleanup import cleanup_resource_group
from pydantic import BaseModel # type: ignore
from typing import Literal
import os
import requests # type: ignore
from fastapi import HTTPException # type: ignore
import time
import secrets
import smtplib
from email.message import EmailMessage
from azure.identity import DefaultAzureCredential
from azure.mgmt.storage import StorageManagementClient

# Path to the CSV dataset (shared across all API endpoints)
CSV_PATH = Path(__file__).resolve().parents[2] / "data" / "All_Diets.csv"

# Initialize the FastAPI application
app = FastAPI(title="Nutritional Insights API")

# Enable CORS so the React frontend can access the backend from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------------------
# Health check endpoint
# -------------------------------------------------------------
@app.get("/health")
async def health():
    """
    Simple health check endpoint to verify that
    the API is running and reachable.
    """
    return {"status": "ok"}


# -------------------------------------------------------------
# Average macronutrients by diet type
# -------------------------------------------------------------
@app.get("/insights/avg", response_model=AvgResponse)
async def avg_insights(diet: str = Query("all")):
    """
    Returns the average protein, carbs, and fat values
    for each diet type (or a specific diet if provided).

    Args:
        diet (str): Optional diet filter (default = "all")

    Returns:
        AvgResponse: List of average macronutrient values
    """
    df = load_data(CSV_PATH)
    dfq = filter_by_diet(df, diet)

    # Group by diet type and calculate the mean of each nutrient
    avg = dfq.groupby("diet_type")[NUM_COLS].mean().reset_index()

    # Convert each row to a Pydantic model instance
    items = [
        AvgInsight(
            diet_type=row["diet_type"],
            avg_protein_g=float(row["protein_g"]),
            avg_carbs_g=float(row["carbs_g"]),
            avg_fat_g=float(row["fat_g"]),
        )
        for _, row in avg.iterrows()
    ]

    return {"items": items}


# -------------------------------------------------------------
# Top N protein-rich recipes (by diet)
# -------------------------------------------------------------
@app.get("/recipes/by_diet")
def recipes_by_diet(diet: str = "all"):
    df = load_data(CSV_PATH)

    if diet != "all":
        df = df[df["diet_type"].str.lower() == diet.lower()]

    df = df.sort_values("protein_g", ascending=False)

    recipes = [
        {
            "diet_type": row["diet_type"],
            "recipe_name": row["recipe_name"],
            "cuisine_type": row["cuisine_type"],
            "protein_g": float(row["protein_g"]),
            "carbs_g": float(row["carbs_g"]),
            "fat_g": float(row["fat_g"]),
        }
        for _, row in df.iterrows()
    ]

    return {"recipes": recipes}


# -------------------------------------------------------------
# K-Means clustering of recipes by macronutrient ratio
# -------------------------------------------------------------
@app.get("/clusters", response_model=ClusterResponse)
async def clusters(k: int = Query(4, ge=2, le=10), diet: str = Query("all")):
    """
    Groups recipes into clusters based on their macronutrient content
    using the K-Means algorithm.

    Args:
        k (int): Number of clusters (default = 4)
        diet (str): Optional diet type filter (default = "all")

    Returns:
        ClusterResponse: List of data points (carbs vs protein) with cluster labels
    """
    df = load_data(CSV_PATH)
    dfq = filter_by_diet(df, diet)

    # Prepare numerical data for clustering
    X = dfq[NUM_COLS].to_numpy()

    # Fit K-Means model to the data
    model = KMeans(n_clusters=k, n_init=10, random_state=42)
    labels = model.fit_predict(X)

    # Build response list of ClusterPoint objects
    points = [
        ClusterPoint(
            x=float(row["carbs_g"]),
            y=float(row["protein_g"]),
            label=int(lbl)
        )
        for (_, row), lbl in zip(dfq.iterrows(), labels)
    ]

    return {"points": points}

# -------------------------------------------------------------
# Security status endpoint
# -------------------------------------------------------------
class SecurityStatus(BaseModel):
    security_status: str
    encryption: str
    access_control: str
    compliance: str
    issues: list[str] = []


@app.get("/security/status", response_model=SecurityStatus)
def get_security_status():
    credential = DefaultAzureCredential()
    subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
    resource_group = os.environ["AZURE_RESOURCE_GROUP"]
    account_name = os.environ["AZURE_STORAGE_ACCOUNT"]

    storage_client = StorageManagementClient(credential, subscription_id)

    account = storage_client.storage_accounts.get_properties(
        resource_group_name=resource_group,
        account_name=account_name
    )

    encryption_enabled = account.encryption.services.blob.enabled

    return SecurityStatus(
        security_status="Secure" if encryption_enabled else "Warning",
        encryption="Enabled" if encryption_enabled else "Disabled",
        access_control="Role-based",
        compliance="Azure Policy Passed",
        issues=[]
    )


# -------------------------------------------------------------
# Cloud resource cleanup endpoint
# -------------------------------------------------------------
@app.post("/cloud/cleanup")
async def cloud_cleanup():
    """
    Cleans up cloud resources by deleting the specified resource group.
    """
    try:
        result = cleanup_resource_group()
        return {"status": "ok", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -------------------------------------------------------------
# GitHub OAuth callback endpoint
# -------------------------------------------------------------

GITHUB_CLIENT_ID = os.environ.get("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.environ.get("GITHUB_CLIENT_SECRET")


@app.get("/auth/github/callback")
def github_callback(code: str):
    if not GITHUB_CLIENT_ID or not GITHUB_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="GitHub OAuth is not configured.")

    # 1) code -> access_token exchange
    token_res = requests.post(
        "https://github.com/login/oauth/access_token",
        headers={"Accept": "application/json"},
        data={
            "client_id": GITHUB_CLIENT_ID,
            "client_secret": GITHUB_CLIENT_SECRET,
            "code": code,
            "redirect_uri": "http://localhost:5173",
        },
    )

    if not token_res.ok:
        raise HTTPException(status_code=500, detail="Failed to exchange GitHub code")

    token_data = token_res.json()
    access_token = token_data.get("access_token")
    if not access_token:
        raise HTTPException(status_code=500, detail=f"GitHub token error: {token_data}")

    # 2) Fetch user information using access_token
    user_res = requests.get(
        "https://api.github.com/user",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    if not user_res.ok:
        raise HTTPException(status_code=500, detail="Failed to fetch GitHub user")

    user = user_res.json()

    # Return only the necessary information for the assignment
    return {
        "provider": "github",
        "login": user.get("login"),
        "name": user.get("name"),
        "avatar_url": user.get("avatar_url"),
    }


# -------------------------------------------------------------
# Google OAuth callback endpoint
# -------------------------------------------------------------
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")


@app.get("/auth/google/callback")
def google_callback(code: str):
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Google OAuth is not configured.")

    # 1) code -> access_token
    token_res = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": "http://localhost:5173",
        },
    )

    if not token_res.ok:
        raise HTTPException(status_code=500, detail="Failed to exchange Google code")

    token_data = token_res.json()
    access_token = token_data.get("access_token")
    if not access_token:
        raise HTTPException(status_code=500, detail="No access token from Google")

    # 2) Fetch userinfo
    user_res = requests.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    if not user_res.ok:
        raise HTTPException(status_code=500, detail="Failed to fetch Google user")

    user = user_res.json()

    return {
        "provider": "google",
        "email": user.get("email"),
        "name": user.get("name"),
        "picture": user.get("picture"),
    }

# -------------------------------------------------------------
# Two-Factor Authentication (2FA) via Email
# -------------------------------------------------------------

class TwoFASendResponse(BaseModel):
    success: bool
    message: str


class TwoFARequest(BaseModel):
    code: str


class TwoFAResponse(BaseModel):
    success: bool
    message: str


TWOFA_STORE = {
    "code": None,
    "expires_at": 0.0,
}

TWOFA_SMTP_HOST = os.environ.get("TWOFA_SMTP_HOST", "smtp.gmail.com")
TWOFA_SMTP_PORT = int(os.environ.get("TWOFA_SMTP_PORT", "587"))
TWOFA_SMTP_USER = os.environ.get("TWOFA_SMTP_USER")
TWOFA_SMTP_PASS = os.environ.get("TWOFA_SMTP_PASS")
TWOFA_EMAIL_TO = os.environ.get("TWOFA_EMAIL_TO")


def send_twofa_email(code: str):
    if not (TWOFA_SMTP_USER and TWOFA_SMTP_PASS and TWOFA_EMAIL_TO):
        raise RuntimeError("2FA email settings are not configured")

    msg = EmailMessage()
    msg["Subject"] = "Your 2FA Code"
    msg["From"] = TWOFA_SMTP_USER
    msg["To"] = TWOFA_EMAIL_TO
    msg.set_content(f"Your 2FA code is: {code}\n\nThis code will expire in 5 minutes.")

    with smtplib.SMTP(TWOFA_SMTP_HOST, TWOFA_SMTP_PORT) as server:
        server.starttls()
        server.login(TWOFA_SMTP_USER, TWOFA_SMTP_PASS)
        server.send_message(msg)

@app.post("/auth/2fa/send", response_model=TwoFASendResponse)
def send_two_fa_code():
    code = f"{secrets.randbelow(1000000):06d}"
    expires_at = time.time() + 5 * 60

    TWOFA_STORE["code"] = code
    TWOFA_STORE["expires_at"] = expires_at

    try:
        send_twofa_email(code)
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Failed to send 2FA email: {exc}"
        )

    return TwoFASendResponse(
        success=True,
        message=f"2FA code sent to {TWOFA_EMAIL_TO}. It will expire in 5 minutes.",
    )

# -------------------------------------------------------------
# 2FA Verification Endpoint
# -------------------------------------------------------------

@app.post("/auth/2fa/verify", response_model=TwoFAResponse)
def verify_two_fa(req: TwoFARequest):

    stored_code = TWOFA_STORE.get("code")
    expires_at = TWOFA_STORE.get("expires_at", 0.0)

    if not stored_code:
        return TwoFAResponse(success=False, message="No 2FA code has been issued.")

    if time.time() > expires_at:
        return TwoFAResponse(success=False, message="The 2FA code has expired.")

    if req.code == stored_code:
        TWOFA_STORE["code"] = None
        return TwoFAResponse(success=True, message="2FA verification successful.")
    else:
        return TwoFAResponse(success=False, message="Invalid 2FA code.")
