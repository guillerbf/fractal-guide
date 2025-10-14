import os
from types import SimpleNamespace

import fractal_guide.services.llm as llm


class DummyMessage:
    def __init__(self, content: str):
        self.content = content


class DummyChoice:
    def __init__(self, text: str):
        self.message = DummyMessage(text)


class DummyResponse:
    def __init__(self, text: str):
        self.choices = [DummyChoice(text)]


def test_summarize_context_success(monkeypatch):
    os.environ["OPENAI_API_KEY"] = "test-key"

    class DummyClient:
        class chat:
            class completions:
                @staticmethod
                def create(**_kwargs):
                    return DummyResponse("Here is a brief overview.")

    monkeypatch.setattr(llm, "OpenAI", lambda api_key=None: DummyClient())

    text, need, options = llm.summarize_context(
        place_text="You're in/near Piazza X",
        user_text="What is this?",
        image_bytes=None,
    )
    assert "overview" in text.lower()
    assert need is False
    assert options == []


def test_summarize_context_missing_key(monkeypatch):
    if "OPENAI_API_KEY" in os.environ:
        del os.environ["OPENAI_API_KEY"]

    text, need, options = llm.summarize_context(
        place_text="You're in/near Piazza X",
        user_text="",
        image_bytes=None,
    )
    assert "not configured" in text.lower()
    assert need is False
    assert options == []


