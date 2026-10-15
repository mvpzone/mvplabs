"""Settings, read from the environment once, at the edge."""

import os
import sys
from dataclasses import dataclass

# The local MCP server, started as a child process from the same virtual environment.
MCP_SERVER = (sys.executable, "-m", "mcpserver.server")


@dataclass(frozen=True)
class Settings:
    model: str = "gemini-3.5-flash"
    mcp_command: tuple[str, ...] = ()  # empty = no MCP tools

    @classmethod
    def from_env(cls) -> "Settings":
        use_mcp = os.environ.get("TIMEKEEPER_USE_MCP", "1") != "0"
        return cls(
            model=os.environ.get("TIMEKEEPER_MODEL", cls.model),
            mcp_command=MCP_SERVER if use_mcp else (),
        )
