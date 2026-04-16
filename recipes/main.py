"""FastAPI entry point for ADK Recipes on Cloud Run / GKE.

Uses ADK's get_fast_api_app() for HTTP serving -- the same pattern as
adk web / adk api_server, but with explicit control over configuration.

Serves all recipes with web UI enabled.
"""

import os

import uvicorn
from google.adk.cli.fast_api import get_fast_api_app

AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
PORT = int(os.environ.get("PORT", "8000"))

app = get_fast_api_app(
    agents_dir=AGENT_DIR,
    web=True,
    a2a=True,
    host="0.0.0.0",
    port=PORT,
    trace_to_cloud=True,
    allow_origins=["*"],
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
