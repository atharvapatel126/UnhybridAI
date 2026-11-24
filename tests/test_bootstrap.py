"""Initialization must never silently restore a user's replaced/deleted policy."""
from dataclasses import replace
from config import load_settings
from scripts import ingest_docs


def test_bootstrap_preserves_replacements_and_deletions(tmp_path, monkeypatch):
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / "Policy.txt").write_text("bundled original policy")
    (raw / "Handbook.txt").write_text("bundled handbook")
    cfg = replace(load_settings({}), raw_docs_dir=raw, chroma_dir=tmp_path / "vectors")
    monkeypatch.setattr(ingest_docs, "settings", cfg)
    monkeypatch.setattr(ingest_docs, "seed_database", lambda: {"ok": True})
    active = {"Policy.txt": "user replacement policy"}
    calls = []
    monkeypatch.setattr(ingest_docs, "list_documents", lambda: [{"source_file": n} for n in active], raising=False)
    def ingest(path):
        calls.append(path.name)
        active[path.name] = path.read_text()
        return {"ok": True, "chunks": 1, "errors": []}
    monkeypatch.setattr(ingest_docs, "ingest_file", ingest)
    assert ingest_docs.main() == 0
    assert active["Policy.txt"] == "user replacement policy"
    assert calls == ["Handbook.txt"]
    del active["Handbook.txt"]
    calls.clear()
    assert ingest_docs.main() == 0
    assert not calls and "Handbook.txt" not in active
    assert ingest_docs.main(["--refresh-fixtures"]) == 0
    assert active["Policy.txt"] == "bundled original policy" and "Handbook.txt" in active


def test_failed_bootstrap_retries_only_missing_files(tmp_path, monkeypatch):
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / "Policy.txt").write_text("bundled original policy")
    cfg = replace(load_settings({}), raw_docs_dir=raw, chroma_dir=tmp_path / "vectors")
    monkeypatch.setattr(ingest_docs, "settings", cfg)
    monkeypatch.setattr(ingest_docs, "seed_database", lambda: {"ok": True})
    monkeypatch.setattr(ingest_docs, "list_documents", lambda: [], raising=False)
    monkeypatch.setattr(ingest_docs, "ingest_file", lambda _: {"ok": False, "errors": ["model unavailable"]})
    assert ingest_docs.main() == 1
    assert not (cfg.chroma_dir / ".fixtures_initialized").exists()
    monkeypatch.setattr(ingest_docs, "ingest_file", lambda _: {"ok": True, "chunks": 1, "errors": []})
    assert ingest_docs.main() == 0
    assert (cfg.chroma_dir / ".fixtures_initialized").exists()
