"""MCP — echo, trace, and time via a custom MCP server on Cloud Run.

Validates token propagation to an IAM-protected Cloud Run MCP server.
Uses ID tokens for Cloud Run auth.

IAM: roles/run.invoker on the SA (+ roles/iap.httpsResourceAccessor if IAP).
Auth: ID token — audience is service URL (Cloud Run IAM) or OAuth client ID (IAP).

Run: adk run recipes/mcp
Web: adk web recipes --port 8888
"""

import os

import google.auth.transport.requests
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset, StreamableHTTPConnectionParams

from .idtoken import acquire_id_token_credentials

MCP_URL = os.environ.get("MCP_URL")
if not MCP_URL:
    raise ValueError(
        "MCP_URL must be set — e.g. https://your-mcp-server-PROJECT.REGION.run.app/mcp"
    )
# Audience: IAP OAuth client ID when behind IAP, service URL otherwise.
MCP_AUDIENCE = os.environ.get(
    "MCP_AUDIENCE",
    MCP_URL.rsplit("/mcp", 1)[0],
)

_id_creds = None

def _get_headers(*args, **kwargs) -> dict[str, str]:
    global _id_creds
    if _id_creds is None:
        _id_creds = acquire_id_token_credentials(MCP_AUDIENCE)
    _id_creds.refresh(google.auth.transport.requests.Request())
    return {"Authorization": f"Bearer {_id_creds.token}"}


root_agent = Agent(
    name="root_agent",
    model="gemini-3-flash-preview",
    description="Test agent for MCP echo, trace, and time tools.",
    instruction=(
        "You are a test assistant. Use the echo tool to echo messages, "
        "the trace tool to inspect HTTP headers, and the time tool to "
        "get the current time. When asked to trace, call the trace tool "
        "and show all headers."
    ),
    tools=[
        McpToolset(
            connection_params=StreamableHTTPConnectionParams(url=MCP_URL),
            header_provider=_get_headers,
        ),
    ],
)
