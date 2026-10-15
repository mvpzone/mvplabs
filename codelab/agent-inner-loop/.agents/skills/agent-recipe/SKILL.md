---
name: agent-recipe
description: House conventions for building a Google ADK agent in Python - one folder per agent, agent / tools / tests split, typed settings read from the environment, hermetic tests with a stub model, an optional local MCP server over stdio, and a Cloud Run deploy under its own least-privilege service account. Use when creating, extending, testing or deploying an ADK agent in this repo, or when asked to scaffold a new agent.
---

# Agent recipe

Build every agent in this repo the same way. A reviewer should find the same files in the same places,
and `uv run pytest` must pass with no network and no credentials.

## Layout (one folder per agent)

```
<agent>/                 # the ADK app: `adk run <agent>`, `adk web .`
  __init__.py            # exactly: from . import agent
  agent.py               # build_agent(settings, model=None) -> Agent; root_agent = build_agent(Settings.from_env())
  config.py              # @dataclass(frozen=True) Settings + Settings.from_env()
  tools.py               # plain functions; docstring = what the model reads
mcpserver/server.py      # optional FastMCP server, stdio, NO __init__.py
tests/                   # conftest.py (stub model + no-network guard), test_tools, test_agent, test_mcpserver
pyproject.toml + uv.lock # exact pins; dev group holds pytest
Dockerfile               # installs from uv.lock, runs as a non-root user
```

## Rules

1. **Settings are typed and read once.** Only `Settings.from_env()` touches `os.environ`. Everything else takes a
   `Settings` argument. No module-level clients, no reading env inside tools.
2. **`build_agent` takes the model as a parameter** so a test can pass a stub. `root_agent` is the only place the real
   model string is used.
3. **Tools are plain functions** with typed arguments, a docstring that says what they return, and a
   `{"status": "success" | "error", ...}` dict. An unknown input returns an error; it never guesses.
4. **Unit tests never call a real model.** Use the `StubLlm` in `tests/conftest.py` (scripted replies) and keep the
   autouse `no_network` fixture. A test that needs the real model is an eval, not a unit test; keep it out of `tests/`.
5. **Every tool gets a direct unit test**, and the agent gets one loop test: stub calls the tool, assert the real tool
   result reached the model's next request.
6. **Deploy with a dedicated service account** holding only `roles/aiplatform.user`. Never the default compute SA.
   Deploy `--no-allow-unauthenticated`.

## Workflow

1. Plan first (`/plan`). The plan names the files above; reject a plan that puts tools in `agent.py` or reads env in
   tools.
2. Write `tools.py` + `test_tools.py`, run `uv run pytest -q`.
3. Write `config.py`, `agent.py`, `test_agent.py`, run the tests again.
4. Only then run against the real model: `uv run adk run <agent>`.

## Gotchas

- **Gemini 3.x models answer only on the global endpoint.** With `GOOGLE_CLOUD_LOCATION=us-central1` they return
  `404 ... Publisher model ... was not found`. Set `GOOGLE_CLOUD_LOCATION=global`. The Cloud Run region is separate.
- **`adk web .` / `adk api_server .` list every folder with an `__init__.py` as an app.** Keep `__init__.py` out of
  `mcpserver/` and `tests/`; start the server with `python -m mcpserver.server` from the project root.
- **The stdio MCP server is a child process.** Start it with `sys.executable` (the same venv), and only print to
  stderr: anything on stdout corrupts the protocol. FastMCP's banner goes away with `mcp.run(show_banner=False)`.
- **Build the image from the lock.** `uv export --frozen --no-dev` then `uv pip install --system`. Installing from
  `pyproject.toml` re-resolves ranges at build time and ships versions you never tested.
- **`gcloud run deploy --source` uploads the folder.** Keep `.venv/`, `.env` and `.adk/` out with `.gcloudignore`
  (`adk run` writes a local session database to `<agent>/.adk/`).
- **A new service account takes a few seconds to exist for IAM.** If the role binding right after
  `gcloud iam service-accounts create` says the account does not exist, wait and retry.
