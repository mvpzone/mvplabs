# hello -- ADK Hello World

Minimal ADK agent with a single tool. Good for validating your setup.

## What It Does

Tells you the current time in major cities using a local Python function (no external APIs needed).

## Run

```bash
# CLI
adk run recipes/hello

# Web UI
adk web recipes --port 8888
# Select "hello" from the agent dropdown
```

## Try

```
What time is it in Tokyo?
What's the time in New York and London?
```

## Requirements

- `google-adk` installed
- A model configured (Gemini via Vertex AI or AI Studio)

No GCP APIs or credentials needed beyond model access.
