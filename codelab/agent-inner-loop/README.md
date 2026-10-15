# agent-inner-loop

The reference solution for the codelab
[Your Agent's Inner Loop: From an Empty Folder to Cloud Run](https://devnull.fyi/labs/your-agents-inner-loop/).

A small [ADK](https://adk.dev) agent, `timekeeper`, that tells the time in a city. It has one local tool
(`lookup_timezone`), one local MCP server over stdio (`echo`, `time`), hermetic tests, and a Cloud Run deploy under
its own service account. The project skill in `.agents/skills/agent-recipe/` is what the coding agent follows.

```
timekeeper/          the agent: agent.py · config.py · tools.py
mcpserver/server.py  the MCP server (stdio)
tests/               stub model + no-network guard, tool / agent / MCP tests
.agents/skills/agent-recipe/SKILL.md
Dockerfile           installs from uv.lock, non-root
```

## Run it

Needs Python 3.13, [uv](https://docs.astral.sh/uv/), and for the model calls a Google Cloud project with Vertex AI
enabled and Application Default Credentials (`gcloud auth application-default login`).

```bash
uv sync
uv run pytest -q                      # no network, no credentials
cp .env.example .env                  # then set GOOGLE_CLOUD_PROJECT
uv run adk run timekeeper             # chat in the terminal
uv run adk web .                      # or the dev UI on http://127.0.0.1:8000
uv run fastmcp list mcpserver/server.py
```

## Deploy it

```bash
PROJECT=your-project-id
gcloud iam service-accounts create timekeeper-run
gcloud projects add-iam-policy-binding $PROJECT \
  --member="serviceAccount:timekeeper-run@$PROJECT.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user" --condition=None
gcloud run deploy timekeeper --source . --region us-central1 \
  --service-account timekeeper-run@$PROJECT.iam.gserviceaccount.com \
  --no-allow-unauthenticated \
  --set-env-vars GOOGLE_CLOUD_PROJECT=$PROJECT,GOOGLE_CLOUD_LOCATION=global
gcloud run services proxy timekeeper --region us-central1 --port 8080
```

Tested 2026-10-15 with google-adk 2.12.0, fastmcp 4.1.0, Python 3.13, `gemini-3.5-flash`.
