"""A stub model: replays scripted replies, records what the agent sent. No network."""

import socket
from collections.abc import AsyncGenerator

import pytest
from google.adk.models import BaseLlm, LlmRequest, LlmResponse
from google.genai import types


class StubLlm(BaseLlm):
    model: str = "stub"
    replies: list[types.Part] = []
    requests: list[LlmRequest] = []

    async def generate_content_async(
        self, llm_request: LlmRequest, stream: bool = False
    ) -> AsyncGenerator[LlmResponse, None]:
        self.requests.append(llm_request)
        part = self.replies.pop(0)
        yield LlmResponse(content=types.Content(role="model", parts=[part]))


def call(name: str, **args) -> types.Part:
    return types.Part(function_call=types.FunctionCall(name=name, args=args))


def say(text: str) -> types.Part:
    return types.Part(text=text)


@pytest.fixture
def stub():
    return StubLlm(replies=[], requests=[])


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    """A unit test that reaches for the network fails loudly instead of calling a real model."""
    def refuse(*args, **kwargs):
        raise RuntimeError("unit tests must not open network connections")

    monkeypatch.setattr(socket.socket, "connect", refuse)
