import os

from azure.identity import AzureCliCredential
from azure.mgmt.resource import ResourceManagementClient


def cleanup_resource_group():

    subscription_id = os.environ.get("AZURE_SUBSCRIPTION_ID")
    resource_group_name = os.environ.get("AZURE_RESOURCE_GROUP")

    if not subscription_id:
        raise RuntimeError("AZURE_SUBSCRIPTION_ID environment variable is not set")
    if not resource_group_name:
        raise RuntimeError("AZURE_RESOURCE_GROUP environment variable is not set")

    credential = AzureCliCredential()

    client = ResourceManagementClient(credential, subscription_id)

    try:
        client.resource_groups.get(resource_group_name)
    except Exception as exc:
        raise RuntimeError(
            f"Resource group '{resource_group_name}' not found or not accessible: {exc}"
        )
    poller = client.resource_groups.begin_delete(resource_group_name)
    poller.result()

    return {"deleted_resource_group": resource_group_name}