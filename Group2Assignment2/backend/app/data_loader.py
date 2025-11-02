import pandas as pd
from pathlib import Path
from .utils import normalize_columns

# Global variable to cache the loaded dataset in memory
# so that the CSV file is not re-read on every API request.
_DATA: pd.DataFrame | None = None


def load_data(csv_path: Path) -> pd.DataFrame:
	"""
	Load and preprocess the dataset from the given CSV path.
	This function reads the data only once and caches it globally.

	Args:
		csv_path (Path): Path to the All_Diets.csv dataset

	Returns:
		pd.DataFrame: Cleaned and normalized DataFrame ready for analysis
	"""
	global _DATA

	# If the dataset is already loaded, return it from memory (cache)
	if _DATA is not None:
		return _DATA

	# Load the CSV file into a pandas DataFrame
	df = pd.read_csv(csv_path)

	# Normalize column names and handle missing values
	df = normalize_columns(df)

	# Cache the processed DataFrame globally for future use
	_DATA = df

	return df