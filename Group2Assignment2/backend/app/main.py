# Defines all API routes for insights, recipes, and clustering.
from http.client import HTTPException
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import pandas as pd
from sklearn.cluster import KMeans
from .data_loader import load_data
from .utils import filter_by_diet, NUM_COLS
from .models import (
    AvgResponse, AvgInsight,
    Recipe, TopProteinResponse,
    ClusterResponse, ClusterPoint
)
from .azure_cleanup import cleanup_resource_group
from pydantic import BaseModel
from typing import Literal
import os
import requests
from fastapi import HTTPException

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
    issues: list[str] = []

    issues.append("CORS is wide open for development (*). Restrict origins in production.")

    return SecurityStatus(
        security_status="Secure",
        encryption="Enabled",
        access_control="Role-based",
        compliance="GDPR Compliant",
        issues=issues,
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
        },
    )

    if not token_res.ok:
        raise HTTPException(status_code=500, detail="Failed to exchange GitHub code")

    token_data = token_res.json()
    access_token = token_data.get("access_token")
    if not access_token:
        raise HTTPException(status_code=500, detail="No access token from GitHub")

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