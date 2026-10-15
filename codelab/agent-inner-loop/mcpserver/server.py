"""A local MCP server over stdio: echo and time."""

import datetime
import zoneinfo

from fastmcp import FastMCP

mcp = FastMCP("clock")


@mcp.tool()
def echo(message: str) -> str:
    """Echo the message back."""
    return message


@mcp.tool()
def time(timezone: str = "UTC") -> str:
    """Return the current time in an IANA time zone, ISO 8601. Unknown zones fall back to UTC."""
    try:
        tz = zoneinfo.ZoneInfo(timezone)
    except (zoneinfo.ZoneInfoNotFoundError, ValueError):
        tz = datetime.timezone.utc
    return datetime.datetime.now(tz).isoformat(timespec="seconds")


if __name__ == "__main__":
    mcp.run(show_banner=False)  # stdio: the agent starts this process and talks over stdin/stdout
