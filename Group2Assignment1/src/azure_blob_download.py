from azure.storage.blob import BlobServiceClient

# Local Azurite connection string
connect_str = "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;" \
              "AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;" \
              "BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"

container_name = "diet-data"
blob_name = "All_Diets.csv"
download_file_path = "outputs/All_Diets_downloaded.csv"

# Connect
blob_service_client = BlobServiceClient.from_connection_string(connect_str)
container_client = blob_service_client.get_container_client(container_name)

# Download the blob
with open(download_file_path, "wb") as f:
    data = container_client.download_blob(blob_name)
    f.write(data.readall())

print(f"Downloaded {blob_name} to {download_file_path}")
