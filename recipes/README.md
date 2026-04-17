# ADK Recipes

Self-contained [Google ADK](https://adk.dev) agent recipes. Each recipe is a single folder you can run locally or deploy to Google Cloud.

## Recipes

| Recipe | Description | Tools | Requirements |
|--------|-------------|-------|-------------|
| [hello](hello/) | Time-telling agent | `get_current_time` (local) | None |
| [search](search/) | Grounded research agent | `google_search` | Vertex AI project |
| [maps](maps/) | Places, weather, and routes | Maps MCP (Grounding Lite) | Vertex AI + Maps API |
| [registry](registry/) | Discover and invoke registered agents | Agent Registry MCP | Vertex AI + Agent Registry API |
| [bigquery](bigquery/) | Query and explore datasets | BigQuery MCP | Vertex AI + BigQuery API |
| [mcp](mcp/) | Custom MCP server on Cloud Run | echo, trace, time (FastMCP) | Vertex AI + Cloud Run MCP server |

## Quick Start

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- Google Cloud SDK (`gcloud`) for Vertex AI recipes

### 1. GCP Setup (for Vertex AI recipes)

```bash
# Authenticate (creates Application Default Credentials)
gcloud auth application-default login

# Enable Vertex AI (required for all recipes except hello)
gcloud services enable aiplatform.googleapis.com

# For maps recipe -- enable Maps MCP
gcloud services enable mapstools.googleapis.com
gcloud services enable cloudapiregistry.googleapis.com

# For registry recipe -- enable Agent Registry
gcloud services enable agentregistry.googleapis.com

# For bigquery recipe -- enable BigQuery
gcloud services enable bigquery.googleapis.com
```

### 2. Install and Configure

```bash
cd recipes
uv venv && source .venv/bin/activate
uv pip install -e .

# Configure environment
cp .env.example .env
# Edit .env -- set GOOGLE_CLOUD_PROJECT to your project ID
```

### 3. Run

```bash
# Web UI -- browse all recipes at http://localhost:8888
adk web . --port 8888

# CLI -- run a specific recipe interactively
adk run hello
adk run maps
```

## Deployment

### Agent Engine

Deploy individual recipes to Vertex AI Agent Engine (managed runtime). See [DEPLOY_AGENT_ENGINE.md](DEPLOY_AGENT_ENGINE.md).

### Cloud Run

All recipes serve from a single container via the ADK FastAPI app (`main.py`).

```bash
# Build and run locally
docker build -t play-recipes .
docker run -p 8000:8000 \
  -e GOOGLE_GENAI_USE_VERTEXAI=1 \
  -e GOOGLE_CLOUD_PROJECT=your-project-id \
  play-recipes

# Deploy to Cloud Run
gcloud run deploy play-recipes \
  --source=. \
  --region=us-central1 \
  --port=8000 \
  --set-env-vars=GOOGLE_GENAI_USE_VERTEXAI=1,GOOGLE_CLOUD_PROJECT=your-project-id,GOOGLE_CLOUD_LOCATION=global
```

## Structure

```
recipes/
  README.md
  pyproject.toml          # dependencies (google-adk, google-auth, uvicorn)
  main.py                 # FastAPI entry point (Cloud Run / GKE)
  Dockerfile              # Container image
  .env.example            # Environment template
  hello/agent.py          # ADK hello world
  search/agent.py         # Google Search grounding
  maps/agent.py           # Maps MCP integration
  registry/agent.py       # Agent Registry MCP
  bigquery/agent.py       # BigQuery MCP
  mcp/agent.py            # Custom MCP server (Cloud Run)
  mcp/idtoken.py          # ID token credential acquisition
```

## Design Principles

- Each recipe is **self-contained** -- one folder, one `agent.py`, runnable standalone
- **No shared framework** -- no base classes, no abstractions until something earns it
- **Preview SDKs welcome** -- pin versions per-recipe if needed
