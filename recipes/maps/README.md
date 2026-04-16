# maps -- Google Maps via MCP

Places, weather, and routes agent powered by Google Maps Platform MCP (Grounding Lite).

## What It Does

Discovers the Maps MCP server from the API Registry and exposes its tools for place search, weather lookup, and route computation. Always includes Google Maps links in responses.

## Run

```bash
# CLI
adk run recipes/maps

# Web UI
adk web recipes --port 8888
# Select "maps" from the agent dropdown
```

## Try

```
Find coffee shops near the Googleplex in Mountain View.
What's the weather in Singapore?
How do I get from SFO airport to downtown San Francisco?
```

## Requirements

- Vertex AI project
- Maps Platform MCP enabled

```bash
# Enable APIs
gcloud services enable aiplatform.googleapis.com
gcloud services enable mapstools.googleapis.com
gcloud services enable cloudapiregistry.googleapis.com

# IAM -- grant your SA the MCP User role
gcloud projects add-iam-policy-binding your-project \
  --member="serviceAccount:your-sa@your-project.iam.gserviceaccount.com" \
  --role="roles/mcp.toolUser"

# Environment
export GOOGLE_GENAI_USE_VERTEXAI=1
export GOOGLE_CLOUD_PROJECT=your-project-id
export GOOGLE_CLOUD_LOCATION=global
```

## Configuration

| Env Var | Default | Description |
|---------|---------|-------------|
| `GOOGLE_CLOUD_PROJECT` | (required) | GCP project with Maps MCP enabled |
| `GOOGLE_CLOUD_LOCATION` | `global` | API Registry location |
| `MAPS_MCP_DIRECT` | unset | Set to `1` to bypass API Registry and use direct MCP URL |
