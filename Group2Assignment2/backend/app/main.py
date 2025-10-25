from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import pandas as pd
from sklearn.cluster import KMeans
from .data_loader import load_data
from .utils import filter_by_diet, NUM_COLS
from .models import AvgResponse, AvgInsight, Recipe, TopProteinResponse, ClusterResponse, ClusterPoint


CSV_PATH = Path(__file__).resolve().parents[2] / "data" / "All_Diets.csv"


app = FastAPI(title="Nutritional Insights API")


app.add_middleware(
CORSMiddleware,
allow_origins=["*"],
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],
)


@app.get("/health")
async def health():
	return {"status": "ok"}


@app.get("/insights/avg", response_model=AvgResponse)
async def avg_insights(diet: str = Query("all")):
	df = load_data(CSV_PATH)
	dfq = filter_by_diet(df, diet)
	avg = dfq.groupby("diet_type")[NUM_COLS].mean().reset_index()
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


@app.get("/recipes/top_protein", response_model=TopProteinResponse)
async def top_protein(diet: str = Query("all"), top: int = Query(5, ge=1, le=50)):
	df = load_data(CSV_PATH)
	dfq = filter_by_diet(df, diet)
	if diet.lower() in ("all", "all diet types"):
		# pick the top N overall when 'all'
		top_df = dfq.sort_values("protein_g", ascending=False).head(top)
		diet_label = "all"
	else:
		top_df = (
			dfq.sort_values("protein_g", ascending=False)
			.head(top)
		)
		diet_label = diet
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


@app.get("/clusters", response_model=ClusterResponse)
async def clusters(k: int = Query(4, ge=2, le=10), diet: str = Query("all")):
	df = load_data(CSV_PATH)
	dfq = filter_by_diet(df, diet)
	X = dfq[NUM_COLS].to_numpy()
	model = KMeans(n_clusters=k, n_init=10, random_state=42)
	labels = model.fit_predict(X)
	points = [
		ClusterPoint(x=float(row["carbs_g"]), y=float(row["protein_g"]), label=int(lbl))
		for (_, row), lbl in zip(dfq.iterrows(), labels)
	]
	return {"points": points}