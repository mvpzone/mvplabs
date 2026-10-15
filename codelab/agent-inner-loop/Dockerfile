FROM python:3.13-slim
COPY --from=ghcr.io/astral-sh/uv:0.12.20 /uv /usr/local/bin/uv
WORKDIR /app

# Install exactly what uv.lock pins (no re-resolve at build time), without the dev group.
COPY pyproject.toml uv.lock ./
RUN uv export --frozen --no-dev --no-emit-project -o /tmp/requirements.txt \
 && uv pip install --system --no-cache -r /tmp/requirements.txt

COPY timekeeper/ timekeeper/
COPY mcpserver/ mcpserver/

RUN useradd --create-home app
USER app

ENV GOOGLE_GENAI_USE_VERTEXAI=1 PYTHONUNBUFFERED=1
CMD ["sh", "-c", "adk api_server --host 0.0.0.0 --port ${PORT:-8080} ."]
