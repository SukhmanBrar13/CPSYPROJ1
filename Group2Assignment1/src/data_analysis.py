import pandas as pd
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "data" / "All_Diets.csv"
OUT_DIR = ROOT / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    def norm(name: str) -> str:
        return str(name).strip().lower().replace(" ", "").replace("(", "").replace(")", "").replace("/", "_")
    df = df.copy()
    df.columns = [norm(c) for c in df.columns]
    return df

def canonicalize(df: pd.DataFrame) -> pd.DataFrame:
    mapping = {
        "diet_type": "Diet_type",
        "recipename": "Recipe_name",
        "recipe_name": "Recipe_name",
        "cuisinetype": "Cuisine_type",
        "cuisine_type": "Cuisine_type",
        "proteing": "Protein_g",
        "protein_g": "Protein_g",
        "carbsg": "Carbs_g",
        "carbs_g": "Carbs_g",
        "fatg": "Fat_g",
        "fat_g": "Fat_g",
    }
    df = df.rename(columns={k: v for k, v in mapping.items() if k in df.columns})
    return df

def main():
    print("[info] reading:", CSV_PATH)
    df = pd.read_csv(CSV_PATH)
    df = normalize_columns(df)
    df = canonicalize(df)

    for col in ["Protein_g", "Carbs_g", "Fat_g"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    for col in ["Protein_g", "Carbs_g", "Fat_g"]:
        df[col].fillna(df[col].mean(), inplace=True)

    avg_macros = df.groupby("Diet_type")[["Protein_g", "Carbs_g", "Fat_g"]].mean().round(2)
    avg_macros.to_csv(OUT_DIR / "insights_by_diet.csv")
    avg_macros.to_json(OUT_DIR / "insights_by_diet.json", orient="index")

    top5 = df.sort_values("Protein_g", ascending=False).groupby("Diet_type").head(5)
    top5.to_csv(OUT_DIR / "top5_protein_by_diet.csv", index=False)
    top5.to_json(OUT_DIR / "top5_protein_by_diet.json", orient="records")

    df["Protein_to_Carbs_ratio"] = df["Protein_g"] / df["Carbs_g"].replace(0, 1)
    df["Carbs_to_Fat_ratio"] = df["Carbs_g"] / df["Fat_g"].replace(0, 1)
    df.head(20).to_csv(OUT_DIR / "sample_with_ratios.csv", index=False)

    print("[done] Preprocessing complete.")

if __name__ == "__main__":
    main()