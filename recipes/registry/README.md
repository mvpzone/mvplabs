# registry -- Agent Registry via MCP

Discover and invoke registered agents through the Agent Registry MCP server.

## What It Does

Connects to the Agent Registry MCP server to list registered agents, inspect their capabilities, and interact with them. Useful for exploring what agents are available in your project.

## Run

```bash
# CLI
adk run recipes/registry

# Web UI
adk web recipes --port 8888
# Select "registry" from the agent dropdown
```

## Try

```
List all registered agents.
What capabilities does the Maps agent have?
```

## Requirements

- Vertex AI project
- Agent Registry API enabled

```bash
# Enable APIs
gcloud services enable aiplatform.googleapis.com
gcloud services enable agentregistry.googleapis.com
gcloud services enable cloudapiregistry.googleapis.com

# IAM -- grant your SA the required roles
gcloud projects add-iam-policy-binding your-project \
  --member="serviceAccount:your-sa@your-project.iam.gserviceaccount.com" \
  --role="roles/agentregistry.viewer"
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
| `GOOGLE_CLOUD_PROJECT` | (required) | GCP project with Agent Registry enabled |
| `GOOGLE_CLOUD_LOCATION` | `global` | Registry location |
| `MCP_SERVER_NAME` | `agentregistry-00000000-0000-0000-3069-c4f146e37652` | MCP server resource name suffix |
