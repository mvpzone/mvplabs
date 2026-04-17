# gcs -- Google Cloud Storage via SDK

List buckets and read objects using the Cloud Storage Python SDK directly (no MCP).

## What It Does

Calls GCS APIs via `google-cloud-storage` client library. Useful for testing whether agent identity (SPIFFE) tokens work with standard GCP client libraries — isolates SDK auth from MCP HTTP auth.

## Run

```bash
# CLI
adk run recipes/gcs

# Web UI
adk web recipes --port 8888
# Select "gcs" from the agent dropdown
```

## Try

```
List all buckets in this project.
List objects in bucket "my-bucket" with prefix "data/".
Read the file "config.json" from bucket "my-bucket".
```

## Requirements

- Vertex AI project
- Cloud Storage API enabled

```bash
# Enable APIs
gcloud services enable aiplatform.googleapis.com
gcloud services enable storage.googleapis.com

# IAM
gcloud projects add-iam-policy-binding your-project \
  --member="serviceAccount:your-sa@your-project.iam.gserviceaccount.com" \
  --role="roles/storage.objectViewer"

# Environment
export GOOGLE_GENAI_USE_VERTEXAI=1
export GOOGLE_CLOUD_PROJECT=your-project-id
```

## Configuration

| Env Var | Default | Description |
|---------|---------|-------------|
| `GOOGLE_CLOUD_PROJECT` | (required) | GCP project for bucket listing |
