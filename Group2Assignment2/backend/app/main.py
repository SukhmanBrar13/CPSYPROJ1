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
@app.get("/recipes/top_protein", response_model=TopProteinResponse)
async def top_protein(diet: str = Query("all"), top: int = Query(5, ge=1, le=50)):
    """
    Returns the top N recipes with the highest protein content.
    Optionally filters by a specific diet type.

    Args:
        diet (str): Diet type to filter by (default = "all")
        top (int): Number of top recipes to return (default = 5)

    Returns:
        TopProteinResponse: List of top recipes with details
    """
    df = load_data(CSV_PATH)
    dfq = filter_by_diet(df, diet)

    # If 'all' diets are selected, get overall top recipes
    if diet.lower() in ("all", "all diet types"):
        top_df = dfq.sort_values("protein_g", ascending=False).head(top)
        diet_label = "all"
    else:
        top_df = dfq.sort_values("protein_g", ascending=False).head(top)
        diet_label = diet

    # Convert to Pydantic model list
    recipes = [
        Recipe(
            diet_type=str(r["diet_type"]),
            recipe_name=str(r["recipe_name"]),
            cuisine_type=str(r.get("cuisine_type", "")),
            protein_g=float(r["protein_g"]),
            carbs_g=float(r["carbs_g"]),
            fat_g=float(r["fat_g"]),
        )
        for _, r in top_df.iterrows()
    ]

    return {"diet_type": diet_label, "recipes": recipes}


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