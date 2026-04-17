# Deploy to Agent Engine

[Agent Engine](https://cloud.google.com/agent-builder/agent-engine) is a managed runtime for ADK agents on Vertex AI. You deploy your agent as a Python object -- Agent Engine handles serving, scaling, and lifecycle.

For full walkthroughs, see:
- [Agent Engine Quickstart](https://docs.cloud.google.com/agent-builder/agent-engine/quickstart)
- [Deploy to Agent Engine](https://docs.cloud.google.com/agent-builder/agent-engine/deploy)

## Prerequisites

- GCP project with `aiplatform.googleapis.com` enabled
- A GCS bucket for staging artifacts
- Python 3.13+ with `google-cloud-aiplatform[adk,agent_engines]` installed

```bash
uv pip install "google-cloud-aiplatform[adk,agent_engines]"
```

## Deploy a Recipe

Agent Engine uses the Python SDK -- there is no `gcloud` CLI for it.

```python
import vertexai
from vertexai.agent_engines import AdkApp

# Import your recipe's root agent
from hello.agent import root_agent

# Initialize Vertex AI
vertexai.init(project="your-project-id", location="us-central1")
client = vertexai.Client(
    project="your-project-id",
    location="us-central1",
    http_options=dict(api_version="v1beta1"),
)

# Wrap in AdkApp
app = AdkApp(agent=root_agent, enable_tracing=True)

# Deploy
result = client.agent_engines.create(
    agent=app,
    config={
        "display_name": "play-hello",
        "requirements": ["google-adk", "google-auth"],
        "extra_packages": ["hello"],
        "staging_bucket": "gs://your-bucket",
        "gcs_dir_name": "play-hello",
        "env_vars": {
            "GOOGLE_CLOUD_LOCATION": "global",
        },
    },
)

print(f"Deployed: {result.api_resource.name}")
```

## Update or Delete

```python
# Find existing by display_name
for ae in client.agent_engines.list(
    config={"filter": 'display_name="play-hello"'}
):
    resource_name = ae.api_resource.name
    break

# Update
client.agent_engines.update(name=resource_name, agent=app, config={...})

# Delete
client.agent_engines.delete(name=resource_name, force=True)
```

## Identity Modes

Agent Engine supports two identity modes:

| Mode | Description | Use Case |
|------|-------------|----------|
| **Service Account** (default) | Runs as a project SA | Get started quickly |
| **Agent Identity** (SPIFFE) | Lifecycle-bound x509 certificate | Fine-grained per-agent IAM |

For agent identity setup and IAM configuration, see [Agent Identity](https://docs.cloud.google.com/agent-builder/agent-engine/agent-identity).

### Agent Identity IAM

Agent identity uses SPIFFE principals. You can grant roles per-agent or project-wide:

```
# Per-agent principal
principal://<trust-domain>/resources/aiplatform/projects/<PROJECT_NUMBER>/locations/<REGION>/reasoningEngines/<AE_ID>

# All agents in project (principalSet)
principalSet://<trust-domain>/attribute.platformContainer/aiplatform/projects/<PROJECT_NUMBER>
```

**Recommended base roles** for agent identity (grant via principalSet for all agents):

- `roles/serviceusage.serviceUsageConsumer`, `roles/browser`
- `roles/logging.logWriter`, `roles/monitoring.metricWriter`, `roles/monitoring.viewer`
- `roles/cloudtrace.agent`, `roles/telemetry.tracesWriter`
- `roles/aiplatform.user`, `roles/aiplatform.sessionUser`, `roles/aiplatform.memoryUser`
- `roles/mcp.toolUser`, `roles/modelarmor.user`
- `roles/agentregistry.viewer`, `roles/cloudapiregistry.viewer`
- `roles/storage.objectViewer`

## Deployment Paths

| Path | Pickle? | Build Control? | Use Case |
|------|---------|---------------|----------|
| Source (`package_spec`) | Yes (cloudpickle) | No | Simple recipes, quick test |
| Dockerfile (`image_spec`) | No | Partial (AE builds) | Custom deps |
| Container (`container_spec`) | No | Full (CI builds) | Pre-built images |

**Source deploy** (cloudpickle) is the most reliable path for simple agents. The Dockerfile and container paths have additional constraints around build conventions and org policies that may cause issues in enterprise environments.

## Key Constraints

| Constraint | Detail |
|------------|--------|
| No HTTP server control | Agent Engine manages the serving layer |
| Prohibited env vars | `GOOGLE_CLOUD_PROJECT`, `PORT` (injected by AE internally) |
| `GOOGLE_CLOUD_LOCATION` | Allowed -- pass via `env_vars` to override AE default |
| Python only | Go/Java/TS ADK agents cannot deploy to AE today |
| Source deploy | Uses `cloudpickle` -- keep dependency graphs simple |
| `InMemoryArtifactService` | Default artifact service -- artifacts lost between requests |
| No VPC | Cannot egress to private network resources |

## Cloud Run Alternative

For full control over HTTP serving, networking, and infrastructure, deploy to Cloud Run instead. See the [Dockerfile](Dockerfile) and [main.py](main.py) in this repo for a ready-to-use pattern.
