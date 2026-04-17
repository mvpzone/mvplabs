# mcpserver -- FastMCP Server on Cloud Run

A minimal [FastMCP](https://github.com/jlowin/fastmcp) server with echo, trace, and time tools. Deploy to Cloud Run as the backend for the [mcp recipe](../mcp/).

## Tools

| Tool | Description |
|------|-------------|
| `echo` | Echo back the input message |
| `trace` | Return all HTTP headers from the incoming request |
| `time` | Return the current time (with optional IANA timezone) |

## Run Locally

```bash
uv pip install "fastmcp>=2.13.1"
python server.py
# MCP server on http://localhost:8080/mcp
```

## Deploy to Cloud Run

```bash
cd mcpserver

# Build and deploy
gcloud run deploy play-mcp \
  --source=. \
  --region=us-central1 \
  --allow-unauthenticated
```

To require authentication (recommended), omit `--allow-unauthenticated` and grant `roles/run.invoker` to calling identities. The [mcp recipe](../mcp/) handles ID token acquisition automatically.
