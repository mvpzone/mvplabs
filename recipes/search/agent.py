"""Google Search — grounded research agent.

Source: https://adk.dev/
Run: adk run recipes/search
Web: adk web recipes --port 8888
"""

from google.adk.agents import Agent
from google.adk.tools import google_search

root_agent = Agent(
    name="root_agent",
    model="gemini-3-flash-preview",
    instruction="You help users research topics thoroughly. "
    "Use Google Search to find current, accurate information.",
    tools=[google_search],
)
