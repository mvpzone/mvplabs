import asyncio
import datetime
import logging
import os
import zoneinfo

from fastmcp import Context, FastMCP

logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)

mcp = FastMCP("MCP Server on Cloud Run")


@mcp.tool()
def echo(message: str) -> str:
    """Echo back the input message.

    Args:
        message: The message to echo back.

    Returns:
        The same message, echoed back.
    """
    logger.info(f"echo called: {message}")
    return message


@mcp.tool()
async def trace(ctx: Context) -> dict:
    """Return all HTTP headers from the incoming request.

    Useful for diagnosing authentication tokens, user-agent,
    and other request metadata.

    Returns:
        A dictionary of all HTTP headers.
    """
    headers = {}
    if ctx.request_context and hasattr(ctx.request_context, "request"):
        headers = dict(ctx.request_context.request.headers)
    logger.info(f"trace called: {list(headers.keys())}")
    return headers


@mcp.tool()
def time(timezone: str = "") -> str:
    """Return the current time.

    Args:
        timezone: IANA timezone name (e.g. 'America/New_York', 'Asia/Tokyo').
                  Defaults to UTC if not specified or invalid.

    Returns:
        The current time in ISO 8601 format with timezone.
    """
    tz = datetime.timezone.utc
    tz_name = timezone.strip() if timezone else "UTC"
    try:
        if tz_name and tz_name != "UTC":
            tz = zoneinfo.ZoneInfo(tz_name)
    except (KeyError, Exception):
        tz_name = "UTC"

    now = datetime.datetime.now(tz).isoformat()
    logger.info(f"time called: {tz_name} -> {now}")
    return now


if __name__ == "__main__":
    logger.info(f"MCP server started on port {os.getenv('PORT', 8080)}")
    asyncio.run(
        mcp.run_async(
            transport="streamable-http",
            host="0.0.0.0",
            port=os.getenv("PORT", 8080),
        )
    )
