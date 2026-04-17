# play-mcp -- FastMCP echo/trace/time server
FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
COPY server.py /app/

ENV PYTHONUNBUFFERED=1

RUN uv pip install --system "fastmcp>=2.13.1"

EXPOSE $PORT

CMD ["python", "server.py"]
