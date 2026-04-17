"""BigQuery — query and explore data via MCP.

Uses the BigQuery remote MCP server directly (no API Registry).
Cross-MCP validation for agent identity (SPIFFE) with Google Cloud MCP.

IAM: roles/mcp.toolUser + roles/bigquery.jobUser + roles/bigquery.dataViewer.
API: bigquery.googleapis.com.
Scopes: cloud-platform (general), bigquery (tool execution).

Run: adk run recipes/bigquery
Web: adk web recipes --port 8888
"""

import os

import google.auth
import google.auth.transport.requests
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset, StreamableHTTPConnectionParams

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")
SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
    "https://www.googleapis.com/auth/bigquery",
]

# Pre-scope ADC — impersonated SAs require explicit scopes to refresh.
# SA creds (Cloud Run / AE) accept scopes silently; user creds ignore them.
_creds, _project = google.auth.default(scopes=SCOPES)
_project_id = PROJECT_ID or _project


def _get_headers(*args, **kwargs) -> dict[str, str]:
    _creds.refresh(google.auth.transport.requests.Request())
    return {"Authorization": f"Bearer {_creds.token}"}


root_agent = Agent(
    name="root_agent",
    model="gemini-3-flash-preview",
    description="Query and explore BigQuery datasets.",
    instruction=(
        "You are a helpful data assistant. Use the BigQuery tools to list datasets, "
        "inspect tables, and run SQL queries. Always show results clearly formatted. "
        f"Default project: {_project_id or 'not set'}."
    ),
    tools=[
        McpToolset(
            connection_params=StreamableHTTPConnectionParams(
                url="https://bigquery.googleapis.com/mcp",
            ),
            header_provider=_get_headers,
        ),
    ],
)
