"""Google Maps — grounded places, weather, and routes via MCP.

Discovers the Maps MCP server from API Registry when GOOGLE_CLOUD_PROJECT
is set. Falls back to direct MCP URL otherwise.

IAM: roles/mcp.toolUser + roles/cloudapiregistry.viewer on the SA.
API: mapstools.googleapis.com + cloudapiregistry.googleapis.com.
Scopes: maps-platform.mapstools (tool execution), cloud-platform (registry).

Run: adk run recipes/maps
Web: adk web recipes --port 8888
"""

import os

import google.auth
import google.auth.transport.requests
from google.adk.agents import Agent
from google.adk.integrations.api_registry import ApiRegistry
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset, StreamableHTTPConnectionParams

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")
MAPS_MCP_SERVER = "google-mapstools.googleapis.com-mcp"
SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
    "https://www.googleapis.com/auth/maps-platform.mapstools",
]

# Pre-scope ADC — impersonated SAs require explicit scopes to refresh.
# SA creds (Cloud Run / AE) accept scopes silently; user creds ignore them.
_creds, _project = google.auth.default(scopes=SCOPES)


def _get_headers(*args, **kwargs) -> dict[str, str]:
    _creds.refresh(google.auth.transport.requests.Request())
    return {"Authorization": f"Bearer {_creds.token}"}


def _build_tools():
    # Direct MCP: agent identity (SPIFFE) or local dev without project.
    # ApiRegistry 401s with agent identity tokens — bypass it.
    if os.environ.get("MAPS_MCP_DIRECT") or not PROJECT_ID:
        return [McpToolset(
            connection_params=StreamableHTTPConnectionParams(url="https://mapstools.googleapis.com/mcp"),
            header_provider=_get_headers,
        )]

    # API Registry: discover MCP servers dynamically.
    # Patch google.auth.default so ApiRegistry.__init__ picks up scoped creds.
    _orig = google.auth.default
    google.auth.default = lambda *a, **kw: (_creds, _project)
    try:
        name = f"projects/{PROJECT_ID}/locations/{LOCATION}/mcpServers/{MAPS_MCP_SERVER}"
        registry = ApiRegistry(PROJECT_ID, location=LOCATION, header_provider=_get_headers)
    finally:
        google.auth.default = _orig
    return [registry.get_toolset(mcp_server_name=name)]


root_agent = Agent(
    name="root_agent",
    model="gemini-3-flash-preview",
    instruction=(
        "You are a helpful travel and places assistant. "
        "Use the Maps tools to search for places, check weather, "
        "and compute routes. Always include Google Maps links when available."
    ),
    tools=_build_tools(),
)
