from dataclasses import replace
import pytest
from config import load_settings
from src import orchestrator
from src.db import queries
from src.db.seed import seed_database


@pytest.fixture
def context(tmp_path, monkeypatch):
    db = tmp_path / "students.db"
    assert seed_database(db)["ok"]
    monkeypatch.setattr(queries, "settings", replace(load_settings({}), db_path=db))
    matches = [{"text": "SYNTHETIC scholarship rule: minimum GPA is 8.0.", "source_file": "policy.txt",
                "page": 1, "chunk_id": "stable-demo-chunk", "score": .8}]
    monkeypatch.setattr(orchestrator, "retrieve", lambda *_: {"matches": matches, "state": "ok", "errors": []})
    return matches


@pytest.mark.parametrize("query,route", [("my GPA", "STRUCTURED"), ("attendance policy", "UNSTRUCTURED"),
    ("Am I eligible for a scholarship?", "HYBRID"), ("cricket match", "OUT_OF_SCOPE")])
def test_routes_and_evidence(context, query, route):
    result = orchestrator.answer_query(query, "S-012", use_llm=False)
    assert result["route"] == route and not result["errors"]
    assert bool(result["evidence"]["sql"]) == (route in ("STRUCTURED", "HYBRID"))
    assert bool(result["evidence"]["docs"]) == (route in ("UNSTRUCTURED", "HYBRID"))
    assert result["timings"]["total_ms"] >= 0 and result["request_id"]
    assert all(item["tag"].startswith("[") for item in result["sources"])


def test_hybrid_isolates_each_failed_branch(context, monkeypatch):
    monkeypatch.setitem(queries.TOOLS, "get_student_profile", lambda *_: (_ for _ in ()).throw(OSError()))
    result = orchestrator.answer_query("Am I eligible for a scholarship?", "S-012", use_llm=False)
    assert result["errors"] and result["evidence"]["docs"] and result["evidence"]["sql"]
    monkeypatch.setattr(orchestrator, "retrieve", lambda *_: (_ for _ in ()).throw(OSError()))
    result = orchestrator.answer_query("Am I eligible for a scholarship?", "S-012", use_llm=False)
    assert result["evidence"]["sql"] and not result["evidence"]["docs"]


def test_missing_unknown_and_empty_documents(context, monkeypatch):
    result = orchestrator.answer_query("Am I eligible for a scholarship?", use_llm=False)
    assert result["evidence"]["docs"] and "Select a synthetic student" in result["errors"][0]
    result = orchestrator.answer_query("my GPA", "S-999", use_llm=False)
    assert not result["evidence"]["sql"] and "No record found" in result["errors"][0]
    monkeypatch.setattr(orchestrator, "retrieve", lambda *_: {"matches": [], "state": "empty", "errors": []})
    assert orchestrator.answer_query("attendance policy", use_llm=False)["errors"]


def test_out_of_scope_and_sql_only_do_not_retrieve(context, monkeypatch):
    monkeypatch.setattr(orchestrator, "retrieve", lambda *_: pytest.fail("Unexpected document retrieval"))
    assert orchestrator.answer_query("cricket", "S-012", use_llm=False)["route"] == "OUT_OF_SCOPE"
    result = orchestrator.answer_query("my department average GPA", "S-012", use_llm=False)
    assert len(result["evidence"]["sql"]) == 2
    assert result["evidence"]["sql"][1]["rows"][0]["dept_id"] == "ME"


def test_only_selected_tools_and_bound_identity(context, monkeypatch):
    called = []
    original = queries.TOOLS["get_student_profile"]
    monkeypatch.setitem(queries.TOOLS, "get_student_profile", lambda sid: (called.append(sid), original(sid))[1])
    monkeypatch.setitem(queries.TOOLS, "get_fee_status", lambda *_: pytest.fail("Unexpected SQL tool"))
    orchestrator.answer_query("my GPA", "S-012", use_llm=False)
    assert called == ["S-012"]
