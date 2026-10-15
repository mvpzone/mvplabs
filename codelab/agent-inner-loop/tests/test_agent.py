"""The agent loop, end to end, against the stub model: the tool really runs, the model never does."""

from google.adk.runners import InMemoryRunner
from google.genai import types

from conftest import call, say
from timekeeper.agent import build_agent
from timekeeper.config import MCP_SERVER, Settings


async def ask(agent, text: str) -> list:
    runner = InMemoryRunner(agent=agent, app_name="test")
    session = await runner.session_service.create_session(app_name="test", user_id="u")
    message = types.Content(role="user", parts=[types.Part(text=text)])
    return [e async for e in runner.run_async(user_id="u", session_id=session.id, new_message=message)]


async def test_agent_calls_the_tool_and_answers(stub):
    stub.replies = [call("lookup_timezone", city="Tokyo"), say("Tokyo is on Asia/Tokyo.")]
    agent = build_agent(Settings(), model=stub)

    events = await ask(agent, "What time zone is Tokyo in?")

    responses = [p.function_response for e in events for p in e.content.parts if p.function_response]
    assert responses[0].response == {"status": "success", "city": "Tokyo", "timezone": "Asia/Tokyo"}
    assert events[-1].content.parts[0].text == "Tokyo is on Asia/Tokyo."
    # The second model call saw the tool's answer.
    assert "Asia/Tokyo" in str(stub.requests[1].contents[-1])


def test_model_comes_from_the_environment(monkeypatch):
    monkeypatch.setenv("TIMEKEEPER_MODEL", "some-other-model")
    assert Settings.from_env().model == "some-other-model"


def test_mcp_is_on_by_default_and_can_be_turned_off(monkeypatch):
    monkeypatch.delenv("TIMEKEEPER_USE_MCP", raising=False)
    assert Settings.from_env().mcp_command == MCP_SERVER
    monkeypatch.setenv("TIMEKEEPER_USE_MCP", "0")
    assert Settings.from_env().mcp_command == ()
