"""Cached CPU embeddings and the ingestion entry point."""
from functools import lru_cache
from hashlib import sha256
import os
from pathlib import Path
import re

from config import settings
from src.ingest.chunk import chunk_pages
from src.ingest.extract import extract_document
from src.ingest.vector_store import DocumentStore

MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
MODEL_REVISION = "1110a243fdf4706b3f48f1d95db1a4f5529b4d41"


@lru_cache(maxsize=1)
def get_model():
    from sentence_transformers import SentenceTransformer
    try:
        return SentenceTransformer(MODEL_ID, device="cpu", revision=MODEL_REVISION,
                                   trust_remote_code=False, cache_folder=str(settings.model_cache),
                                   local_files_only=os.getenv("HF_HUB_OFFLINE") == "1")
    except Exception:
        raise RuntimeError("Embedding model unavailable. Download it with network access first, or check the model cache.") from None


def embed_texts(texts):
    if not texts:
        return []
    return get_model().encode(texts, batch_size=32, normalize_embeddings=True,
                              show_progress_bar=False).tolist()


def ingest_file(path, *, store=None):
    extracted = extract_document(path)
    if extracted["errors"]:
        return {"ok": False, "chunks": 0, "errors": extracted["errors"]}
    try:
        # Publication dates belong to their page/paragraph, never ingestion time.
        pages = []
        for page in extracted["pages"]:
            for paragraph in re.split(r"\n\s*\n", page["text"]):
                dated = dict(page, text=paragraph)
                for label, key in (("Published", "published_at"), ("Effective", "effective_from")):
                    match = re.search(label + r":\s*(\d{4}-\d{2}-\d{2})", paragraph)
                    if match:
                        dated[key] = match[1]
                pages.append(dated)
        chunks = chunk_pages(pages, settings.chunk_size, settings.chunk_overlap)
        if not chunks:
            return {"ok": False, "chunks": 0, "errors": ["Document has no text chunks of at least 30 characters."]}
        fingerprint = sha256(Path(path).read_bytes()).hexdigest()
        vectors = embed_texts([chunk["text"] for chunk in chunks])
        return (store or DocumentStore()).publish(Path(path).name, fingerprint, chunks, vectors)
    except Exception:
        return {"ok": False, "chunks": 0, "errors": ["Ingestion failed. Check embedding model availability and vector-store access; existing indexed content is retained."]}


def list_documents():
    return DocumentStore().list_documents()


def delete_document(name):
    from src.ingest.extract import validate_filename
    if not validate_filename(name):
        return {"ok": False, "error": "Invalid document name."}
    try:
        return {"ok": DocumentStore().delete_document(name), "error": None}
    except Exception:
        return {"ok": False, "error": "Unable to delete document from index."}
