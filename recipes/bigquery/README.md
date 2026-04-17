# bigquery -- BigQuery via MCP

Query and explore BigQuery datasets through the BigQuery remote MCP server.

## What It Does

Connects directly to the BigQuery MCP server (no API Registry) to list datasets, inspect tables, and run SQL queries. Also serves as cross-MCP validation for agent identity (SPIFFE) with Google Cloud MCP.

## Run

```bash
# CLI
adk run recipes/bigquery

# Web UI
adk web recipes --port 8888
# Select "bigquery" from the agent dropdown
```

## Try

```
List all datasets in this project.
Show me the schema for the session_events_log table.
Run a query to count rows in the last 24 hours.
```

## Requirements

- Vertex AI project
- BigQuery API enabled

```bash
# Enable APIs
gcloud services enable aiplatform.googleapis.com
gcloud services enable bigquery.googleapis.com

# IAM -- grant your SA the required roles
gcloud projects add-iam-policy-binding your-project \
  --member="serviceAccount:your-sa@your-project.iam.gserviceaccount.com" \
  --role="roles/mcp.toolUser"
gcloud projects add-iam-policy-binding your-project \
  --member="serviceAccount:your-sa@your-project.iam.gserviceaccount.com" \
  --role="roles/bigquery.jobUser"
gcloud projects add-iam-policy-binding your-project \
  --member="serviceAccount:your-sa@your-project.iam.gserviceaccount.com" \
  --role="roles/bigquery.dataViewer"

# Environment
export GOOGLE_GENAI_USE_VERTEXAI=1
export GOOGLE_CLOUD_PROJECT=your-project-id
```

## Configuration

| Env Var | Default | Description |
|---------|---------|-------------|
| `GOOGLE_CLOUD_PROJECT` | (required) | GCP project with BigQuery data |
