import math
from pathlib import Path

import pytest
from src.ingest import embed_store
from src.ingest.vector_store import DocumentStore
from src.rag import retriever


def fake_embeddings(texts):
    return [[1., 0., 0.] if "scholarship" in text.lower() else [0., 1., 0.] for text in texts]


@pytest.fixture
def store(tmp_path, monkeypatch):
    monkeypatch.setattr(embed_store, "embed_texts", fake_embeddings)
    monkeypatch.setattr(retriever, "embed_texts", fake_embeddings)
    return DocumentStore(tmp_path / "vectors")


def test_persist_reingest_replace_and_delete(store, tmp_path):
    path = tmp_path / "policy.txt"
    path.write_text("Scholarship policy has merit criteria and a December deadline. " * 25)
    assert embed_store.ingest_file(path, store=store)["ok"]
    before = store.collection.count()
    assert embed_store.ingest_file(path, store=store)["unchanged"]
    assert store.collection.count() == before
    reopened = DocumentStore(store.path)
    result = retriever.retrieve("scholarship", store=reopened)
    assert result["state"] == "ok" and result["matches"][0]["score"] == pytest.approx(1.)
    path.write_text("Scholarship revised deadline and new merit policy. " * 2)
    assert embed_store.ingest_file(path, store=store)["ok"]
    assert store.collection.count() < before
    assert all("revised" in item["text"] for item in retriever.retrieve("scholarship", store=store)["matches"])
    assert retriever.retrieve("unrelated", store=store)["state"] == "no_match"
    assert store.delete_document(path.name) and not store.list_documents()
    assert store.collection.count() == 0


def test_failed_replacement_preserves_previous(store, tmp_path, monkeypatch):
    path = tmp_path / "policy.txt"
    path.write_text("Scholarship original policy and original deadline statement.")
    assert embed_store.ingest_file(path, store=store)["ok"]
    previous = store.manifest()
    path.write_text("Scholarship replacement policy and replacement deadline statement.")
    def fail_commit(_):
        raise OSError("simulated full disk")
    monkeypatch.setattr(store, "_commit", fail_commit)
    assert not embed_store.ingest_file(path, store=store)["ok"]
    assert store.manifest() == previous
    assert "original" in retriever.retrieve("scholarship", store=store)["matches"][0]["text"]
    path.write_text("")
    assert not embed_store.ingest_file(path, store=store)["ok"]
    assert store.manifest() == previous


def test_inactive_vectors_are_never_returned(store, tmp_path, monkeypatch):
    path = tmp_path / "policy.txt"
    path.write_text("Scholarship old version with a conflicting old deadline.")
    assert embed_store.ingest_file(path, store=store)["ok"]
    monkeypatch.setattr(store.collection, "delete", lambda **kwargs: (_ for _ in ()).throw(OSError("cleanup failure")))
    path.write_text("Scholarship new version with a clearly revised deadline.")
    result = embed_store.ingest_file(path, store=store)
    assert result["ok"] and result["errors"]
    assert all("new version" in m["text"] for m in retriever.retrieve("scholarship", store=store)["matches"])


def test_partial_staging_failure_keeps_old_revision(store, tmp_path, monkeypatch):
    path = tmp_path / "policy.txt"
    path.write_text("Scholarship original statement remains available after failed indexing.")
    assert embed_store.ingest_file(path, store=store)["ok"]
    upsert = store.collection.upsert
    def partial_write(**kwargs):
        upsert(**kwargs)
        raise OSError("write interrupted after partial staging")
    monkeypatch.setattr(store.collection, "upsert", partial_write)
    monkeypatch.setattr(store.collection, "delete", lambda **_: (_ for _ in ()).throw(OSError("cleanup failed")))
    path.write_text("Scholarship staged statement must never replace the active original.")
    assert not embed_store.ingest_file(path, store=store)["ok"]
    assert all("original statement" in m["text"] for m in retriever.retrieve("scholarship", store=store)["matches"])


def test_empty_invalid_and_embedding_failure(store, tmp_path, monkeypatch):
    assert retriever.retrieve("query", store=store)["state"] == "empty"
    assert retriever.retrieve("", store=store)["state"] == "no_match"
    assert retriever.retrieve("query", threshold="bad", store=store)["state"] == "error"
    assert embed_store.embed_texts([]) == []
    path = tmp_path / "policy.txt"
    path.write_text("Scholarship policy with an explicit merit eligibility rule.")
    monkeypatch.setattr(embed_store, "embed_texts", lambda _: (_ for _ in ()).throw(RuntimeError("offline")))
    assert not embed_store.ingest_file(path, store=store)["ok"]
    assert not store.list_documents()


@pytest.mark.model
def test_real_embeddings_and_fixture_retrieval(tmp_path):
    from config import settings
    vectors = embed_store.embed_texts(["merit scholarship deadline", "scholarship application closing date", "volcano lava eruption"])
    assert len(vectors[0]) == 384
    assert math.sqrt(sum(x*x for x in vectors[0])) == pytest.approx(1., abs=1e-5)
    dot = lambda a, b: sum(x*y for x, y in zip(a, b))
    assert dot(vectors[0], vectors[1]) > dot(vectors[0], vectors[2])
    assert embed_store.get_model() is embed_store.get_model()
    store = DocumentStore(tmp_path / "real-vectors")
    for path in settings.raw_docs_dir.iterdir():
        if path.suffix in (".pdf", ".txt"):
            assert embed_store.ingest_file(path, store=store)["ok"]
    results = retriever.retrieve("merit scholarship application deadline", k=3, store=store)
    assert "Scholarship_Policy.pdf" in [m["source_file"] for m in results["matches"]]
    assert not retriever.retrieve("quantum black hole stellar supernova", store=store)["matches"]
    assert any(m["page"] == 4 for m in retriever.retrieve("minimum exam attendance", store=store)["matches"])
