from azure.storage.blob import BlobServiceClient # type: ignore
import importlib
import io
import json
from pathlib import Path

CONNECT_STR = (
    "DefaultEndpointsProtocol=http;"
    "AccountName=devstoreaccount1;"
    "AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;"
    "BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"
)
CONTAINER = "diet-data"
BLOB_NAME = "All_Diets.csv"
OUT_DIR = Path("simulated_nosql")
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT_DIR / "results.json"

_pd = None
_blob_service = None

def get_pd():
    global _pd
    if _pd is None:
        _pd = importlib.import_module("pandas")
    return _pd

def get_blob_service():
    global _blob_service
    if _blob_service is None:
        _blob_service = BlobServiceClient.from_connection_string(CONNECT_STR)
    return _blob_service

def handler(event=None, context=None):
    pd = get_pd()
    svc = get_blob_service()

    blob = svc.get_blob_client(container=CONTAINER, blob=BLOB_NAME)
    data = blob.download_blob().readall()
    df = pd.read_csv(io.BytesIO(data))

    cols = {c.lower().replace("(", "").replace(")", ""): c for c in df.columns}
    def pick(*names):
        for n in names:
            key = n.lower()
            if key in cols:
                return cols[key]
        return None

    diet_col = pick("diet_type")
    prot_col = pick("protein_g", "proteing", "protein g")
    carb_col = pick("carbs_g", "carbsg", "carbs g")
    fat_col  = pick("fat_g", "fatg", "fat g")

    if any(x is None for x in [diet_col, prot_col, carb_col, fat_col]):
        raise RuntimeError(f"Missing expected columns. Found: {list(df.columns)}")

    avg = df.groupby(diet_col)[[prot_col, carb_col, fat_col]].mean().reset_index()
    result = avg.to_dict(orient="records")

    with open(OUT_JSON, "w") as f:
        json.dump(result, f, indent=2)

    return {"ok": True, "rows": len(result), "out": str(OUT_JSON)}

if __name__ == "__main__":
    print(handler())
