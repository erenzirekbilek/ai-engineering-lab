"""chat() istek govdesini dogru kuruyor mu - sahte istemciyle, ag olmadan."""

from types import SimpleNamespace

import pytest

from tools import llm
from tools.config import Settings

SETTINGS = Settings(
    api_key="test-key",
    model="gemini-3.8-flash",
    temperature=0.3,
    max_output_tokens=256,
)


class FakeInteractions:
    def __init__(self):
        self.last_kwargs = None

    def create(self, **kwargs):
        self.last_kwargs = kwargs
        return SimpleNamespace(
            output_text="merhaba",
            id="int_123",
            usage=SimpleNamespace(
                total_input_tokens=10,
                total_output_tokens=20,
                total_thought_tokens=5,
                total_tokens=35,
            ),
        )


@pytest.fixture
def fake_client(monkeypatch):
    interactions = FakeInteractions()
    monkeypatch.setattr(llm, "get_client", lambda settings=None: SimpleNamespace(interactions=interactions))
    monkeypatch.setattr(llm, "log_event", lambda *a, **k: None)
    return interactions


def test_temperature_is_omitted_for_models_that_ignore_it(fake_client):
    llm.chat("selam", settings=SETTINGS, model="gemini-3.8-flash", temperature=0.9)
    config = fake_client.last_kwargs["generation_config"]
    assert "temperature" not in config
    assert config["max_output_tokens"] == 256


def test_temperature_is_sent_for_models_that_support_it(fake_client):
    llm.chat("selam", settings=SETTINGS, model="gemini-3.5-flash-lite", temperature=0.9)
    assert fake_client.last_kwargs["generation_config"]["temperature"] == 0.9


def test_temperature_falls_back_to_settings_value(fake_client):
    llm.chat("selam", settings=SETTINGS, model="gemini-3.5-flash-lite")
    assert fake_client.last_kwargs["generation_config"]["temperature"] == 0.3


def test_optional_fields_are_omitted_when_not_given(fake_client):
    llm.chat("selam", settings=SETTINGS)
    assert "system_instruction" not in fake_client.last_kwargs
    assert "previous_interaction_id" not in fake_client.last_kwargs


def test_optional_fields_are_passed_through(fake_client):
    llm.chat(
        "selam",
        settings=SETTINGS,
        system_instruction="kisa konus",
        previous_interaction_id="int_000",
    )
    assert fake_client.last_kwargs["system_instruction"] == "kisa konus"
    assert fake_client.last_kwargs["previous_interaction_id"] == "int_000"


def test_usage_is_mapped_and_thought_tokens_are_billed_as_output(fake_client):
    result = llm.chat("selam", settings=SETTINGS, model="gemini-3.8-flash")

    assert result.text == "merhaba"
    assert result.interaction_id == "int_123"
    assert (result.input_tokens, result.output_tokens, result.thought_tokens) == (10, 20, 5)
    assert result.total_tokens == 35

    # 10 input * 0.75 + (20 + 5) output * 3.75, 1M token basina
    expected = (10 * 0.75 + 25 * 3.75) / 1_000_000
    assert result.cost_usd == pytest.approx(expected)


def test_missing_api_key_raises_readable_error(monkeypatch):
    monkeypatch.setattr(llm, "log_event", lambda *a, **k: None)
    empty = Settings(api_key=None, model="gemini-3.8-flash", temperature=1.0, max_output_tokens=128)
    with pytest.raises(llm.LabError, match="GEMINI_API_KEY"):
        llm.chat("selam", settings=empty)
