from azure.storage.blob import BlobServiceClient
import pandas as pd
import io
import json
import os

# Connection string to local Azurite
connect_str = (
    "DefaultEndpointsProtocol=http;"
    "AccountName=devstoreaccount1;"
    "AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;"
    "BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"
)


blob_service_client = BlobServiceClient.from_connection_string(connect_str)
container_name = "diet-data"
blob_name = "All_Diets.csv"
local_csv_path = r"C:\proj1\Group2Assignment1\data\All_Diets.csv"


# 1 Create container if it doesn't exist
try:
    blob_service_client.create_container(container_name)
    print(f"Container '{container_name}' created.")
except Exception:
    print(f"Container '{container_name}' already exists or creation skipped.")

# 2 Upload CSV to container
blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
with open(local_csv_path, "rb") as data:
    blob_client.upload_blob(data, overwrite=True)
print(f"CSV '{blob_name}' uploaded successfully.")

# 3 Download CSV and process it
stream = blob_client.download_blob().readall()
df = pd.read_csv(io.BytesIO(stream))

# 4 Calculate averages
avg_macros = df.groupby("Diet_type")[["Protein(g)", "Carbs(g)", "Fat(g)"]].mean()

# 5 Save results to simulated NoSQL JSON
os.makedirs("simulated_nosql", exist_ok=True)
results_path = "simulated_nosql/results.json"
result = avg_macros.reset_index().to_dict(orient="records")
with open(results_path, "w") as f:
    json.dump(result, f, indent=4)

print(f" Data processed and stored successfully at '{results_path}'")
print("Preview of results (first few rows):")
print(result[:5])
