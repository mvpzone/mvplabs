"""GCS — list buckets and read objects via the Cloud Storage SDK.

Tests Google Cloud SDK API calls (not MCP). Useful for validating whether
agent identity (SPIFFE) tokens work with standard GCP client libraries.

IAM: roles/storage.objectViewer (read objects), roles/storage.admin (list buckets).
API: storage.googleapis.com.

Run: adk run recipes/gcs
Web: adk web recipes --port 8888
"""

import os

from google.adk.agents import Agent
from google.cloud import storage

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")


def list_buckets(project: str = "") -> list[str]:
    """List all GCS buckets in the project.

    Args:
        project: GCP project ID. Uses default if not specified.

    Returns:
        List of bucket names.
    """
    client = storage.Client(project=project or PROJECT_ID)
    return [b.name for b in client.list_buckets()]


def list_objects(bucket_name: str, prefix: str = "", max_results: int = 20) -> list[str]:
    """List objects in a GCS bucket.

    Args:
        bucket_name: Name of the GCS bucket.
        prefix: Optional prefix to filter objects.
        max_results: Maximum number of objects to return.

    Returns:
        List of object names.
    """
    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=prefix or None, max_results=max_results)
    return [b.name for b in blobs]


def read_object(bucket_name: str, object_name: str) -> str:
    """Read a text object from GCS.

    Args:
        bucket_name: Name of the GCS bucket.
        object_name: Full path of the object in the bucket.

    Returns:
        The object contents as text (first 4KB).
    """
    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(object_name)
    return blob.download_as_text()[:4096]


root_agent = Agent(
    name="root_agent",
    model="gemini-3-flash-preview",
    description="List buckets and read objects from Google Cloud Storage.",
    instruction=(
        "You are a storage assistant. Use the tools to list buckets, "
        "list objects in a bucket, and read text files. "
        f"Default project: {PROJECT_ID or 'not set'}."
    ),
    tools=[list_buckets, list_objects, read_object],
)
