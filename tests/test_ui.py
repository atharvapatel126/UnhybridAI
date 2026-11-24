from dataclasses import replace
from pathlib import Path
from streamlit.testing.v1 import AppTest
from config import load_settings
from src import orchestrator
from src.ui import sidebar


def prepare(monkeypatch, *, empty=False):
    monkeypatch.setattr(sidebar, "settings", replace(load_settings({}), api_key=""))
    monkeypatch.setattr(sidebar, "list_students", lambda: {
        "rows": [] if empty else [{"student_id": "S-012", "name": "Demo Student 12"}, {"student_id": "S-001", "name": "Demo Student 01"}],
        "error": "Database unavailable" if empty else None})
    monkeypatch.setattr(sidebar, "list_documents", lambda: [])
    return AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=15).run()


def test_startup_missing_key_empty_stores(monkeypatch):
    app = prepare(monkeypatch, empty=True)
    assert not app.exception
    text = " ".join(item.value for item in app.info)
    assert "Gemini key not configured" in text and "No documents indexed" in text
    assert any("Student database unavailable" in item.value for item in app.warning)


def test_student_identity_history_and_mode(monkeypatch):
    calls = []
    def answer(query, student_id, **kwargs):
        calls.append((query, student_id, kwargs))
        return {"route": "STRUCTURED", "reason": "Test evidence", "method": "fallback",
            "answer": "GPA 8.4 [SQL-1]", "errors": [], "sources": [{"tag": "[SQL-1]", "source": "SQL:students"}],
            "evidence": {"sql": [{"tag": "[SQL-1]", "source": "SQL:students", "rows": [{"gpa": 8.4}]}], "docs": []},
            "timings": {"total_ms": 1}, "generation_method": "evidence"}
    monkeypatch.setattr(orchestrator, "answer_query", answer)
    app = prepare(monkeypatch)
    app.sidebar.selectbox[0].set_value("S-012").run()
    app.chat_input[0].set_value("What is my GPA?").run()
    assert not app.exception
    assert calls == [("What is my GPA?", "S-012", {"use_llm": False})]
    assert len(app.session_state["messages"]) == 1
    assert any(item.label == "SQL evidence" for item in app.expander)
    app.sidebar.selectbox[0].set_value("S-001").run()
    assert not app.session_state["messages"]
    assert len(calls) == 1  # A rerender must not regenerate an answer.


def test_generated_answer_warnings_and_document_panels(monkeypatch):
    def answer(*args, **kwargs):
        return {"route": "UNSTRUCTURED", "reason": "Document policy", "method": "llm",
            "answer": "Attendance is 75 percent [DOC-1].", "errors": ["Partial evidence warning"],
            "sources": [{"tag": "[DOC-1]", "source_file": "rules.pdf", "page": 4}],
            "evidence": {"sql": [], "docs": [{"tag": "[DOC-1]", "source_file": "rules.pdf", "page": 4,
                "text": "75 percent attendance.", "score": .8, "published_at": "2026-09-01"}]},
            "timings": {"total_ms": 100}, "generation_method": "generated"}
    monkeypatch.setattr(orchestrator, "answer_query", answer)
    app = prepare(monkeypatch)
    app.chat_input[0].set_value("Attendance policy?").run()
    assert not app.exception
    assert any(item.label == "Document evidence" for item in app.expander)
    assert any("Partial evidence warning" in item.value for item in app.warning)
