"""The MCP server, in memory: no subprocess, no network."""

from fastmcp import Client

from mcpserver.server import mcp


async def test_lists_both_tools():
    async with Client(mcp) as client:
        names = {t.name for t in await client.list_tools()}
    assert names == {"echo", "time"}


async def test_time_in_a_zone():
    async with Client(mcp) as client:
        result = await client.call_tool("time", {"timezone": "Asia/Tokyo"})
    assert result.data.endswith("+09:00")
