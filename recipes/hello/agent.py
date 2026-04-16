"""Hello World — ADK get-started validation.

Source: https://adk.dev/get-started/python/
Run: adk run recipes/hello
Web: adk web recipes --port 8888
"""

from google.adk.agents.llm_agent import Agent


def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city."""
    import datetime

    tz_map = {
        "new york": "America/New_York",
        "london": "Europe/London",
        "tokyo": "Asia/Tokyo",
        "sydney": "Australia/Sydney",
        "singapore": "Asia/Singapore",
    }
    tz_name = tz_map.get(city.lower(), "UTC")
    tz = datetime.timezone.utc
    try:
        import zoneinfo
        tz = zoneinfo.ZoneInfo(tz_name)
    except Exception:
        pass

    now = datetime.datetime.now(tz)
    return {
        "status": "success",
        "city": city,
        "time": now.strftime("%I:%M %p"),
        "timezone": tz_name,
    }


root_agent = Agent(
    model="gemini-3-flash-preview",
    name="root_agent",
    description="Tells the current time in a specified city.",
    instruction="You are a helpful assistant that tells the current time in cities. "
    "Use the 'get_current_time' tool for this purpose.",
    tools=[get_current_time],
)
