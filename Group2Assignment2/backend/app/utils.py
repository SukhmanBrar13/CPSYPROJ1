# provides helper functions to clean and filter the dataset
import pandas as pd
from typing import List

# -------------------------------------------------------------
# Utility functions for data cleaning and filtering
# -------------------------------------------------------------

# Column name mapping to normalize inconsistent headers in the CSV file
NORMALIZE_MAP = {
    "Protein(g)": "protein_g",
    "Carbs(g)": "carbs_g",
    "Fat(g)": "fat_g",
    "Diet_type": "diet_type",
    "Recipe_name": "recipe_name",
    "Cuisine_type": "cuisine_type",
}

# List of numerical columns used for calculations and clustering
NUM_COLS = ["protein_g", "carbs_g", "fat_g"]


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans and standardizes the input DataFrame:
      - Renames inconsistent column headers to snake_case
      - Converts text columns to lowercase and strips whitespace
      - Converts numeric columns to floats and fills missing values with column means

    Args:
        df (pd.DataFrame): Raw dataset loaded from CSV

    Returns:
        pd.DataFrame: Cleaned and normalized DataFrame
    """
    # Rename columns based on predefined mapping
    df = df.rename(columns={k: v for k, v in NORMALIZE_MAP.items() if k in df.columns})

    # Normalize text fields: lowercase and trim extra spaces
    if "diet_type" in df.columns:
        df["diet_type"] = df["diet_type"].astype(str).str.lower().str.strip()
    if "cuisine_type" in df.columns:
        df["cuisine_type"] = df["cuisine_type"].astype(str).str.lower().str.strip()

    # Ensure numeric fields are numeric and handle invalid entries
    present_num_cols = [c for c in NUM_COLS if c in df.columns]
    for c in present_num_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # Fill any missing numeric values with the mean of the column
    if present_num_cols:
        df[present_num_cols] = df[present_num_cols].fillna(
            df[present_num_cols].mean(numeric_only=True)
        )

    return df


def filter_by_diet(df: pd.DataFrame, diet: str) -> pd.DataFrame:
    """
    Filters the dataset by a specific diet type.
    If "all" or an empty string is provided, returns the original dataset.

    Args:
        df (pd.DataFrame): Normalized DataFrame
        diet (str): Diet type filter (e.g., "keto", "paleo", or "all")

    Returns:
        pd.DataFrame: Filtered DataFrame containing only the selected diet
    """
    if not diet or diet.lower() in ("all", "all diet types"):
        return df

    if "diet_type" not in df.columns:
        return df

    # Return a copy of rows matching the selected diet type
    return df[df["diet_type"].str.lower() == diet.lower()].copy()