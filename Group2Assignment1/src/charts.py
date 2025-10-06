import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "data" / "All_Diets.csv"
OUT_DIR = ROOT / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    def norm(name: str) -> str:
        s = str(name)
        s = s.replace("(", "").replace(")", "")
        s = s.replace("/", "_").replace("-", "_")
        s = s.replace(" ", "")
        return s.strip().lower()
    out = df.copy()
    out.columns = [norm(c) for c in out.columns]
    return out


def canonicalize(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {
        "diet_type": "Diet_type",
        "recipe_name": "Recipe_name",
        "recipename": "Recipe_name",
        "cuisine_type": "Cuisine_type",
        "cuisinetype": "Cuisine_type",
        "proteing": "Protein_g",
        "protein_g": "Protein_g",
        "protein g": "Protein_g",
        "carbsg": "Carbs_g",
        "carbs_g": "Carbs_g",
        "fatg": "Fat_g",
        "fat_g": "Fat_g",
    }
    present = {k: v for k, v in rename_map.items() if k in df.columns}
    return df.rename(columns=present)


def load_data() -> pd.DataFrame:
    df = pd.read_csv(CSV_PATH)
    df = normalize_columns(df)
    df = canonicalize(df)

    # numeric cast
    for c in ["Protein_g", "Carbs_g", "Fat_g"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # drop rows missing essentials
    df = df.dropna(subset=["Diet_type", "Recipe_name", "Protein_g", "Carbs_g", "Fat_g"])
    return df


def main():
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df = load_data()

    # 1) Bar chart: average macros by diet type
    avg_macros = (
        df.groupby("Diet_type")[["Protein_g", "Carbs_g", "Fat_g"]]
        .mean()
        .round(2)
        .sort_index()
    )

    plt.figure()
    avg_macros.plot(kind="bar")  # matplotlib default colors, single figure
    plt.title(f"Average Macronutrients by Diet Type\n{ts}")
    plt.ylabel("Grams")
    plt.xlabel("Diet Type")
    plt.tight_layout()
    bar_path = OUT_DIR / "chart_bar_avg_macros_by_diet.png"
    plt.savefig(bar_path, dpi=140)
    plt.close()

    # 2) Scatter plot: top 5 protein-rich recipes per diet (distribution by recipe)
    top5 = (
        df.sort_values("Protein_g", ascending=False)
          .groupby("Diet_type", group_keys=False)
          .head(5)
    )

    plt.figure()
    # one-color scatter (no explicit color choices)
    plt.scatter(top5["Protein_g"], top5["Carbs_g"], alpha=0.6)
    plt.title(f"Top-5 Protein-Rich Recipes per Diet (Scatter)\n{ts}")
    plt.xlabel("Protein (g)")
    plt.ylabel("Carbs (g)")
    plt.tight_layout()
    scatter_path = OUT_DIR / "chart_scatter_top5_protein_recipes.png"
    plt.savefig(scatter_path, dpi=140)
    plt.close()

    # 3) Heatmap: correlation among macros (Protein/Carbs/Fat)
    corr = df[["Protein_g", "Carbs_g", "Fat_g"]].corr()

    plt.figure()
    plt.imshow(corr, interpolation="nearest")
    plt.title(f"Nutrient Correlation Heatmap\n{ts}")
    plt.colorbar()
    ticks = range(len(corr.columns))
    plt.xticks(ticks, corr.columns, rotation=45, ha="right")
    plt.yticks(ticks, corr.columns)
    plt.tight_layout()
    heatmap_path = OUT_DIR / "chart_heatmap_corr.png"
    plt.savefig(heatmap_path, dpi=140)
    plt.close()

    print("[done] charts saved:")
    print(" -", bar_path)
    print(" -", scatter_path)
    print(" -", heatmap_path)


if __name__ == "__main__":
    main()
