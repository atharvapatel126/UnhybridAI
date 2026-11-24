"""Persistent Chroma vectors with atomic active-revision publication per document.

New vectors remain invisible until the manifest commits. Stale cleanup failure
cannot expose superseded chunks. One process owns writes in this local demo.
"""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import threading

from config import settings

LOCK = threading.RLock()


class DocumentStore:
    def __init__(self, path=None):
        import chromadb
        from chromadb.config import Settings
        self.path = Path(path or settings.chroma_dir)
        self.path.mkdir(parents=True, exist_ok=True)
        self.manifest_path = self.path / "documents.json"
        self.client = chromadb.PersistentClient(str(self.path), settings=Settings(anonymized_telemetry=False))
        self.collection = self.client.get_or_create_collection(
            "unihybrid-chunks", embedding_function=None,
            configuration={"hnsw": {"space": "cosine"}},
        )

    def manifest(self):
        if not self.manifest_path.exists():
            return {}
        return json.loads(self.manifest_path.read_text(encoding="utf-8"))

    def _commit(self, documents):
        temporary = self.manifest_path.with_suffix(".pending")
        temporary.write_text(json.dumps(documents, ensure_ascii=False), encoding="utf-8")
        temporary.replace(self.manifest_path)

    def publish(self, name, fingerprint, chunks, vectors):
        with LOCK:
            documents = self.manifest()
            old = documents.get(name)
            if old and old["fingerprint"] == fingerprint:
                return {"ok": True, "chunks": old["chunks"], "unchanged": True, "errors": []}
            revision = sha256(f"{name}:{fingerprint}".encode()).hexdigest()
            timestamp = datetime.now(timezone.utc).isoformat()
            ids = [f"{revision}:{chunk['chunk_id']}" for chunk in chunks]
            metadata = [{k: v for k, v in chunk.items() if k != "text"} | {
                "doc_revision": revision, "ingested_at": timestamp,
            } for chunk in chunks]
            try:
                for offset in range(0, len(chunks), 128):
                    stop = offset + 128
                    self.collection.upsert(ids=ids[offset:stop], embeddings=vectors[offset:stop],
                                           documents=[c["text"] for c in chunks[offset:stop]],
                                           metadatas=metadata[offset:stop])
                documents[name] = {"source_file": name, "revision": revision,
                                   "fingerprint": fingerprint, "chunks": len(chunks), "ingested_at": timestamp}
                self._commit(documents)
            except Exception:
                # Manifest still points to the old revision; staged chunks are not queried.
                try:
                    self.collection.delete(where={"doc_revision": revision})
                except Exception:
                    pass
                raise
            errors = []
            if old:
                try:
                    self.collection.delete(where={"doc_revision": old["revision"]})
                except Exception:
                    errors.append("Document updated; inactive old vectors could not be cleaned up.")
            return {"ok": True, "chunks": len(chunks), "unchanged": False, "errors": errors}

    def list_documents(self):
        with LOCK:
            return sorted(self.manifest().values(), key=lambda item: item["source_file"])

    def delete_document(self, name):
        with LOCK:
            documents = self.manifest()
            old = documents.pop(name, None)
            if not old:
                return False
            self._commit(documents)
            self.collection.delete(where={"source_file": name})
            return True

    def search(self, vector, k):
        with LOCK:
            revisions = [item["revision"] for item in self.manifest().values()]
            if not revisions:
                return None
            return self.collection.query(query_embeddings=[vector], n_results=min(k, self.collection.count()),
                                         where={"doc_revision": {"$in": revisions}},
                                         include=["documents", "metadatas", "distances"])
