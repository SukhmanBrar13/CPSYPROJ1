import pandas as pd
from typing import List


NORMALIZE_MAP = {
	"Protein(g)": "protein_g",
	"Carbs(g)": "carbs_g",
	"Fat(g)": "fat_g",
	"Diet_type": "diet_type",
	"Recipe_name": "recipe_name",
	"Cuisine_type": "cuisine_type",
}


NUM_COLS = ["protein_g", "carbs_g", "fat_g"]


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
	df = df.rename(columns={k: v for k, v in NORMALIZE_MAP.items() if k in df.columns})
	if "diet_type" in df.columns:
		df["diet_type"] = df["diet_type"].astype(str).str.lower().str.strip()
	if "cuisine_type" in df.columns:
		df["cuisine_type"] = df["cuisine_type"].astype(str).str.lower().str.strip()

	present_num_cols = [c for c in NUM_COLS if c in df.columns]
	for c in present_num_cols:
		df[c] = pd.to_numeric(df[c], errors="coerce")
	if present_num_cols:
		df[present_num_cols] = df[present_num_cols].fillna(df[present_num_cols].mean(numeric_only=True))
	return df


def filter_by_diet(df: pd.DataFrame, diet: str) -> pd.DataFrame:
	if not diet or diet.lower() in ("all", "all diet types"):
		return df
	if "diet_type" not in df.columns:
		return df
	return df[df["diet_type"].str.lower() == diet.lower()].copy()