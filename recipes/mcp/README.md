# mcp -- Custom MCP Server (Cloud Run)

Connect an ADK agent to your own MCP server on Cloud Run with ID token authentication.

## What It Does

Connects to a custom FastMCP server on Cloud Run with echo, trace, and time tools. Uses ID tokens for Cloud Run IAM authentication. The trace tool echoes all HTTP headers, useful for validating token propagation.

## Run

```bash
# CLI
adk run recipes/mcp

# Web UI
adk web recipes --port 8888
# Select "mcp" from the agent dropdown
```

## Try

```
Echo "hello from the agent".
Trace -- show me all the HTTP headers.
What time is it in America/New_York?
```

## Requirements

- Vertex AI project
- A FastMCP server deployed on Cloud Run (see `mcpserver/` in the source repo for an example)

```bash
# IAM -- grant your SA the Cloud Run invoker role
gcloud projects add-iam-policy-binding your-project \
  --member="serviceAccount:your-sa@your-project.iam.gserviceaccount.com" \
  --role="roles/run.invoker"

# Environment
export GOOGLE_GENAI_USE_VERTEXAI=1
export GOOGLE_CLOUD_PROJECT=your-project-id

# Local dev -- impersonate an SA with run.invoker
gcloud auth application-default login \
  --impersonate-service-account=your-sa@your-project.iam.gserviceaccount.com
```

## Configuration

| Env Var | Default | Description |
|---------|---------|-------------|
| `MCP_URL` | (required) | Your Cloud Run MCP server endpoint |
| `MCP_AUDIENCE` | Service URL (derived from `MCP_URL`) | IAP OAuth client ID when behind IAP |
