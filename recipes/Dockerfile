# Cloud Run / GKE — pyful-play recipes
#
# Aligned to ADK GKE pattern: get_fast_api_app() + uvicorn.
# Serves all recipes with web UI + A2A enabled.
#
# Build:
#   docker build -t play .
#   docker run -p 8000:8000 -e GOOGLE_GENAI_USE_VERTEXAI=1 play

ARG PYTHON_VERSION=3.13
FROM python:${PYTHON_VERSION}-slim
WORKDIR /app

RUN adduser --disabled-password --gecos "" appuser

# Install uv for fast dependency resolution
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install deps from lockfile
COPY --chown=appuser:appuser pyproject.toml uv.lock /app/
RUN uv pip install --system --no-cache -r pyproject.toml

USER appuser
ENV PATH="/home/appuser/.local/bin:$PATH"

COPY --chown=appuser:appuser recipes/ /app/recipes/
COPY --chown=appuser:appuser main.py /app/main.py

ENV GOOGLE_GENAI_USE_VERTEXAI=1

EXPOSE 8000

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
