import pandas as pd
from pathlib import Path
from .utils import normalize_columns


_DATA: pd.DataFrame | None = None


def load_data(csv_path: Path) -> pd.DataFrame:
	global _DATA
	if _DATA is not None:
		return _DATA
	df = pd.read_csv(csv_path)
	df = normalize_columns(df)
	_DATA = df
	return df