# search -- Grounded Research Agent

Research agent with Google Search grounding. Answers questions using current web information.

## What It Does

Uses Gemini's built-in `google_search` tool to find and synthesize current information from the web.

## Run

```bash
# CLI
adk run recipes/search

# Web UI
adk web recipes --port 8888
# Select "search" from the agent dropdown
```

## Try

```
What are the latest developments in AI agent frameworks?
Compare Cloud Run and Cloud Functions for serving AI agents.
```

## Requirements

- Vertex AI project with `aiplatform.googleapis.com` enabled
- Application Default Credentials (`gcloud auth application-default login`)

```bash
export GOOGLE_GENAI_USE_VERTEXAI=1
export GOOGLE_CLOUD_PROJECT=your-project-id
```
