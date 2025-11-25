import os
from azure.identity import ClientSecretCredential
from azure.mgmt.resource import ResourceManagementClient


def cleanup_resource_group():

    subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
    tenant_id = os.environ["AZURE_TENANT_ID"]
    client_id = os.environ["AZURE_CLIENT_ID"]
    client_secret = os.environ["AZURE_CLIENT_SECRET"]

    # put real resource group name here
    resource_group_name = os.environ.get("AZURE_RESOURCE_GROUP", "lab3-rg")

    credential = ClientSecretCredential(
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret=client_secret,
    )

    client = ResourceManagementClient(credential, subscription_id)

    poller = client.resource_groups.begin_delete(resource_group_name)
    poller.result()

    return {"deleted_resource_group": resource_group_name}