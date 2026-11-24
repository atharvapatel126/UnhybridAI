from dataclasses import replace
from types import SimpleNamespace

import pytest
from config import load_settings
from src.llm import gemini_client as client


class UpstreamError(Exception):
    def __init__(self, code):
        self.code = code
        super().__init__("do-not-expose-private-sentinel")


@pytest.fixture
def sdk(monkeypatch):
    state = {"responses": [], "calls": [], "options": None, "sleeps": [], "events": [], "closed": False}
    monkeypatch.setattr(client, "settings", replace(load_settings({}), api_key="do-not-expose-private-sentinel"))
    monkeypatch.setattr(client.time, "sleep", state["sleeps"].append)
    monkeypatch.setattr(client, "event", lambda name, **fields: state["events"].append(fields))
    class FakeClient:
        def __init__(self, **kwargs):
            state["options"] = kwargs["http_options"]
            self.models = self
        def __enter__(self):
            return self
        def __exit__(self, *args):
            state["closed"] = True
        def generate_content(self, **kwargs):
            state["calls"].append(kwargs)
            item = state["responses"].pop(0)
            if isinstance(item, Exception):
                raise item
            return item
    monkeypatch.setattr(client.genai, "Client", FakeClient)
    return state


def response(text="OK", **kwargs):
    return SimpleNamespace(text=text, usage_metadata=None, candidates=[], **kwargs)


def test_success_and_sdk_budget(sdk):
    sdk["responses"] = [response('{"status":"ok"}')]
    schema = {"type": "object", "properties": {"status": {"type": "string"}}, "required": ["status"]}
    assert client.generate("prompt", system="rules", json_mode=True, response_schema=schema) == '{"status":"ok"}'
    assert sdk["options"].timeout == 15000 and sdk["options"].retry_options.attempts == 1
    assert sdk["options"].api_version == "v1"
    assert sdk["calls"][0]["config"].response_mime_type == "application/json"
    assert sdk["calls"][0]["config"].response_json_schema == schema
    assert sdk["closed"] and sdk["events"][0]["attempts"] == 1


@pytest.mark.parametrize("code", [429, 500, 503])
def test_bounded_retries(sdk, code):
    sdk["responses"] = [UpstreamError(code)] * 3
    with pytest.raises(client.LLMUnavailable):
        client.generate("prompt")
    assert len(sdk["calls"]) == 3 and sdk["sleeps"] == [1, 2]
    assert [item["code"] for item in sdk["events"][0]["attempt_errors"]] == [code] * 3
    assert sdk["closed"]


def test_retry_recovers(sdk):
    sdk["responses"] = [UpstreamError(429), response()]
    assert client.generate("prompt") == "OK"
    assert sdk["sleeps"] == [1]


@pytest.mark.parametrize("exception", [UpstreamError(400), UpstreamError(401), UpstreamError(403),
                                       UpstreamError(404), TimeoutError("private"), ConnectionError("private")])
def test_permanent_and_network_errors_do_not_retry(sdk, exception):
    sdk["responses"] = [exception]
    with pytest.raises(client.LLMUnavailable) as error:
        client.generate("prompt")
    assert "private" not in str(error.value)
    assert len(sdk["calls"]) == 1 and not sdk["sleeps"]


@pytest.mark.parametrize("text,json_mode", [(None, False), ("", False), ("not json", True)])
def test_bad_response(sdk, text, json_mode):
    sdk["responses"] = [response(text)]
    with pytest.raises(client.LLMBadResponse):
        client.generate("prompt", json_mode=json_mode)
    assert len(sdk["calls"]) == 1


@pytest.mark.parametrize("prompt_blocked", [True, False])
def test_blocked_and_missing_key(sdk, monkeypatch, prompt_blocked):
    blocked = response("blocked", prompt_feedback=SimpleNamespace(block_reason="SAFETY" if prompt_blocked else None))
    if not prompt_blocked:
        blocked.candidates = [SimpleNamespace(finish_reason="SAFETY")]
    sdk["responses"] = [blocked]
    with pytest.raises(client.LLMBadResponse, match="blocked"):
        client.generate("prompt")
    monkeypatch.setattr(client, "settings", load_settings({}))
    with pytest.raises(client.LLMUnavailable, match="GEMINI_API_KEY"):
        client.generate("prompt")
    assert len(sdk["calls"]) == 1


def test_redacted_prompt_and_response_usage(sdk):
    sentinel = client.settings.api_key
    result = response(sentinel)
    usage = {"prompt_token_count": 3, "candidates_token_count": 2}
    result.usage_metadata = SimpleNamespace(model_dump=lambda **_: usage)
    sdk["responses"] = [result]
    client.generate(sentinel, system=sentinel)
    assert sentinel not in str(sdk["events"])
    assert sdk["events"][0]["usage"] == usage
