"""Agent Registry — discover and invoke agents via MCP.

Discovers the Agent Registry MCP server and exposes its tools
for listing, inspecting, and interacting with registered agents.

IAM: roles/agentregistry.viewer + roles/mcp.toolUser on the SA.
API: agentregistry.googleapis.com + cloudapiregistry.googleapis.com.
Scopes: cloud-platform (registry), maps-platform.mapstools (MCP tool execution).

Run: adk run recipes/registry
Web: adk web recipes --port 8888
"""

import os

import google.auth
import google.auth.transport.requests
from google.adk.agents import Agent
from google.adk.integrations.agent_registry import AgentRegistry

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")
MCP_SERVER_NAME = os.environ.get(
    "MCP_SERVER_NAME",
    "agentregistry-00000000-0000-0000-3069-c4f146e37652",
)
SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
    "https://www.googleapis.com/auth/maps-platform.mapstools",
]

# Pre-scope ADC — impersonated SAs require explicit scopes to refresh.
# SA creds (Cloud Run / AE) accept scopes silently; user creds ignore them.
_creds, _project = google.auth.default(scopes=SCOPES)
_project_id = PROJECT_ID or _project


def _get_headers(*args, **kwargs) -> dict[str, str]:
    _creds.refresh(google.auth.transport.requests.Request())
    return {"Authorization": f"Bearer {_creds.token}"}


def _build_tools():
    # Patch google.auth.default so AgentRegistry.__init__ picks up scoped creds.
    # header_provider gives AgentRegistrySingleMcpToolset scoped tokens at runtime.
    _orig = google.auth.default
    google.auth.default = lambda *a, **kw: (_creds, _project_id)
    try:
        registry = AgentRegistry(
            project_id=_project_id,
            location=LOCATION,
            header_provider=_get_headers,
        )
        name = f"projects/{_project_id}/locations/{LOCATION}/mcpServers/{MCP_SERVER_NAME}"
        return [registry.get_mcp_toolset(name)]
    finally:
        google.auth.default = _orig


root_agent = Agent(
    name="root_agent",
    model="gemini-3-flash-preview",
    instruction=(
        "You are a helpful assistant for managing and discovering AI agents. "
        "Use the Agent Registry tools to list registered agents, inspect their "
        "capabilities, and help users understand what agents are available."
    ),
    tools=_build_tools(),
)
