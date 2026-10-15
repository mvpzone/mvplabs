"""The agent: built from Settings, so a test can build it with a stub model."""

from google.adk.agents import Agent
from google.adk.models import BaseLlm
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters

from .config import Settings
from .tools import lookup_timezone

INSTRUCTION = """You tell people the time in cities.
1. Call lookup_timezone with the city.
2. If it succeeds, call the time tool with that time zone and answer with the local time.
3. If the city is unknown, say so. Never guess a time."""


def build_agent(settings: Settings, model: str | BaseLlm | None = None) -> Agent:
    tools: list = [lookup_timezone]
    if settings.mcp_command:
        command, *args = settings.mcp_command
        tools.append(
            McpToolset(
                connection_params=StdioConnectionParams(
                    server_params=StdioServerParameters(command=command, args=args),
                    timeout=10,
                ),
                tool_filter=["time", "echo"],
            )
        )
    return Agent(
        name="timekeeper",
        model=model or settings.model,
        description="Tells the current time in a city.",
        instruction=INSTRUCTION,
        tools=tools,
    )


root_agent = build_agent(Settings.from_env())
