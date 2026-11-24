import json
from pathlib import Path
import pytest
from src.router import classifier

CASES = [case for case in json.loads(Path(__file__).with_name("eval_set.json").read_text()) if case["split"] == "tuning"]


@pytest.mark.parametrize("case", CASES, ids=lambda c: c["id"])
def test_labeled_fallback_routes(case):
    result = classifier.classify(case["query"], use_llm=False)
    assert result["route"] == case["expected_route"]
    assert set(result["sql_tools"]) == set(case["expected_tools"])
    assert result["method"] == "fallback"


@pytest.mark.parametrize("case", CASES, ids=lambda c: c["id"])
def test_mocked_llm_contract(case, monkeypatch):
    expected = {"route": case["expected_route"], "sql_tools": case["expected_tools"],
                "doc_query": case["query"] if case["expected_source_file"] else "", "reason": "Mocked route contract"}
    monkeypatch.setattr(classifier, "generate", lambda *a, **k: json.dumps(expected))
    result = classifier.classify(case["query"])
    assert result["route"] == expected["route"] and result["method"] == "llm"


@pytest.mark.parametrize("payload", ["not json", "[]", "null",
    '{"route":"HACK","sql_tools":[],"doc_query":"","reason":"bad"}',
    '{"route":"STRUCTURED","sql_tools":["execute_sql"],"doc_query":"","reason":"bad"}',
    '{"route":"STRUCTURED","sql_tools":["get_student_profile"],"doc_query":"","reason":"bad","student_id":"S-999"}',
    '{"route":"OUT_OF_SCOPE","sql_tools":["get_student_profile"],"doc_query":"","reason":"bad"}',
    '{"route":"STRUCTURED","sql_tools":["get_department_stats"],"doc_query":"","reason":"bad"}',
])
def test_bad_llm_outputs_use_fallback(monkeypatch, payload):
    monkeypatch.setattr(classifier, "generate", lambda *a, **k: payload)
    assert classifier.classify("What is my GPA?")["method"] == "fallback"


def test_api_failure_and_empty_query(monkeypatch):
    monkeypatch.setattr(classifier, "generate", lambda *a, **k: (_ for _ in ()).throw(TimeoutError()))
    assert classifier.classify("my fees")["route"] == "STRUCTURED"
    assert classifier.classify("")["route"] == "OUT_OF_SCOPE"
    assert classifier.classify("a" * 2001)["route"] == "OUT_OF_SCOPE"


def test_personal_scholarship_always_fetches_current_fees(monkeypatch):
    incomplete = {"route": "HYBRID", "sql_tools": ["get_student_profile"],
                  "doc_query": "scholarship criteria deadline", "reason": "Incomplete model tool set"}
    monkeypatch.setattr(classifier, "generate", lambda *a, **k: json.dumps(incomplete))
    result = classifier.classify("Am I eligible for a merit scholarship?")
    assert result["method"] == "fallback"
    assert set(result["sql_tools"]) == {"get_student_profile", "get_fee_status"}
