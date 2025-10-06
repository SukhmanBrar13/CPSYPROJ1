from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import os

# Azurite local connection string
connect_str = "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;" \
              "AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;" \
              "BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"

# Create the BlobServiceClient
blob_service_client = BlobServiceClient.from_connection_string(connect_str)

# Container name
container_name = "diet-data"

try:
    container_client = blob_service_client.create_container(container_name)
    print(f"Container '{container_name}' created")
except Exception as e:
    print(f"Container may already exist: {e}")

# File path to upload
file_path = os.path.join("data", "All_Diets.csv")
blob_name = "All_Diets.csv"

# Create a blob client
blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

# Upload the file
with open(file_path, "rb") as data:
    blob_client.upload_blob(data, overwrite=True)
    print(f"Uploaded {file_path} to container '{container_name}' as blob '{blob_name}'")

# List blobs in the container
print("\nBlobs in container:")
blobs = blob_service_client.get_container_client(container_name).list_blobs()
for blob in blobs:
    print(" -", blob.name)
