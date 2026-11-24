from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import datetime
import json
from types import SimpleNamespace

from config import load_settings
from src import orchestrator
from src.db import queries
from src.db.seed import seed_database
from src.llm import gemini_client
from src.utils import logger


def lines(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_utf8_redaction_usage_and_context_reset(monkeypatch):
    secret = "dummy-private-log-sentinel"
    monkeypatch.setattr(logger, "settings", replace(logger.settings, api_key=secret))
    with logger.request_context("trace-one"):
        assert logger.event("llm_call", prompt="हिन्दी " + secret, system="rules",
            response=secret, headers={"authorization": "another-private-secret"},
            usage={"prompt_token_count": 9}, attempts=1, error=None) is None
    assert logger.current_request_id() is None
    path = logger.settings.logs_dir / "prompts.jsonl"
    text = path.read_text(encoding="utf-8")
    record = lines(path)[0]
    assert secret not in text and "another-private-secret" not in text
    assert "हिन्दी" in text and record["usage"]["prompt_token_count"] == 9
    assert record["schema_version"] == 1 and record["request_id"] == "trace-one"
    assert datetime.fromisoformat(record["timestamp"]).tzinfo is not None


def test_rotation_retention_and_no_partial_json(monkeypatch):
    sentinel = "dummy-rotation-sentinel"
    monkeypatch.setattr(logger, "settings", replace(logger.settings, api_key=sentinel, log_max_bytes=1024, log_backups=2))
    for sequence in range(20):
        assert logger.event("execution", query="synthetic question " * 20 + sentinel, sequence=sequence) is None
    files = list(logger.settings.logs_dir.glob("execution.jsonl*"))
    assert len(files) == 3
    for path in files:
        assert path.stat().st_size <= 1024 and lines(path)
        assert sentinel not in path.read_text(encoding="utf-8")
    assert lines(logger.settings.logs_dir / "execution.jsonl")[-1]["sequence"] == 19


def test_threaded_writes_remain_valid():
    def write(index):
        assert logger.event("execution", query=f"Question {index}", request_id=f"thread-{index}") is None
    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(write, range(80)))
    records = lines(logger.settings.logs_dir / "execution.jsonl")
    assert len(records) == 80 and len({record["request_id"] for record in records}) == 80


def test_execution_projects_chunk_provenance():
    logger.event("execution", route="UNSTRUCTURED", method="fallback", sql_tools=[], errors=[],
        evidence={"docs": [{"chunk_id":"chunk-1", "source_file":"policy.txt", "page":2, "score":.8, "text":"full text is not copied to execution summary"}]})
    record = lines(logger.settings.logs_dir / "execution.jsonl")[0]
    assert record["retrieved_chunks"] == [{"chunk_id":"chunk-1", "source_file":"policy.txt", "page":2, "score":.8}]
    assert "evidence" not in record


def test_oversized_record_never_written(monkeypatch):
    monkeypatch.setattr(logger, "settings", replace(logger.settings, log_max_bytes=1024))
    assert "Logging unavailable" in logger.event("llm_call", prompt="x" * 2048)
    assert not (logger.settings.logs_dir / "prompts.jsonl").exists()


def test_log_failure_does_not_destroy_answer(tmp_path, monkeypatch):
    db = tmp_path / "demo.db"
    assert seed_database(db)["ok"]
    monkeypatch.setattr(queries, "settings", replace(load_settings({}), db_path=db))
    blocked = tmp_path / "not-a-directory"
    blocked.write_text("file")
    monkeypatch.setattr(logger, "settings", replace(logger.settings, logs_dir=blocked))
    result = orchestrator.answer_query("my GPA", "S-012", use_llm=False)
    assert "8.4" in result["answer"]
    assert any("Logging unavailable" in error for error in result["errors"])


def test_two_calls_correlate_and_out_of_scope_has_none(tmp_path, monkeypatch):
    db = tmp_path / "demo.db"
    assert seed_database(db)["ok"]
    monkeypatch.setattr(queries, "settings", replace(load_settings({}), db_path=db))
    monkeypatch.setattr(gemini_client, "settings", replace(load_settings({}), api_key="dummy-sdk-key"))
    replies = iter([
        json.dumps({"route":"STRUCTURED", "sql_tools":["get_student_profile", "get_fee_status"], "doc_query":"", "reason":"Records"}),
        json.dumps({"answer":"GPA 8.4 [SQL-1]; current fees Paid [SQL-2].", "reasoning":"These are retrieved records [SQL-1][SQL-2].", "missing_information":"None identified."}),
    ])
    class FakeClient:
        def __init__(self, **kwargs):
            self.models = self
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
        def generate_content(self, **kwargs):
            return SimpleNamespace(text=next(replies), candidates=[], usage_metadata=None)
    monkeypatch.setattr(gemini_client.genai, "Client", FakeClient)
    result = orchestrator.answer_query("What is my GPA and fee status?", "S-012")
    assert result["generation_method"] == "generated"
    execution = lines(logger.settings.logs_dir / "execution.jsonl")
    prompts = lines(logger.settings.logs_dir / "prompts.jsonl")
    assert len(execution) == 1 and len(prompts) == 2
    assert {record["request_id"] for record in [*execution, *prompts]} == {result["request_id"]}
    assert execution[0]["student_id"] == "S-012" and execution[0]["completion_state"] == "completed"
    assert "sql_ms" in execution[0]["timings"] and prompts[1]["response_schema"]
    assert "dummy-sdk-key" not in (logger.settings.logs_dir / "prompts.jsonl").read_text()
    out = orchestrator.answer_query("cricket", use_llm=False)
    assert out["route"] == "OUT_OF_SCOPE"
    assert len(lines(logger.settings.logs_dir / "execution.jsonl")) == 2
    assert len(lines(logger.settings.logs_dir / "prompts.jsonl")) == 2


def test_prompt_write_failure_warning_propagates(tmp_path, monkeypatch):
    db = tmp_path / "demo.db"
    assert seed_database(db)["ok"]
    monkeypatch.setattr(queries, "settings", replace(load_settings({}), db_path=db))
    original = logger._append
    def append(path, record):
        if path.name == "prompts.jsonl":
            raise OSError("simulated disk failure")
        original(path, record)
    monkeypatch.setattr(logger, "_append", append)
    # Simulate the client log call inside the classifier while preserving valid routing.
    def classify(*args, **kwargs):
        logger.event("llm_call", prompt="prompt", response="route")
        return {"route":"STRUCTURED", "sql_tools":["get_student_profile"], "doc_query":"", "reason":"Fallback", "method":"fallback"}
    monkeypatch.setattr(orchestrator, "classify", classify)
    result = orchestrator.answer_query("my GPA", "S-012", use_llm=False)
    assert "8.4" in result["answer"] and any("Logging unavailable" in e for e in result["errors"])
    assert lines(logger.settings.logs_dir / "execution.jsonl")[0]["completion_state"] == "completed_with_warnings"
