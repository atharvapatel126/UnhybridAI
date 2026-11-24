"""Measure valid-file ingestion and deliberate invalid inputs in an isolated store."""
from time import perf_counter
from uuid import uuid4
from config import settings
from src.ingest.embed_store import ingest_file
from src.ingest.vector_store import DocumentStore


def measure_ingestion(output):
    directory = output / f"ingestion-probe-{uuid4().hex[:8]}"
    directory.mkdir()
    store = DocumentStore(directory / "vectors")
    files = [(path, True) for path in sorted(settings.raw_docs_dir.iterdir()) if path.suffix.lower() in (".pdf", ".txt", ".md")]
    for name, content in (("corrupt.pdf", b"not a PDF"), ("empty.txt", b""), ("unsupported.csv", b"a,b")):
        path = directory / name
        path.write_bytes(content)
        files.append((path, False))
    results = []
    for path, valid in files:
        start = perf_counter()
        result = ingest_file(path, store=store)
        results.append({"file": path.name, "expected_valid": valid, "ok": result["ok"],
                        "chunks": result["chunks"], "errors": result["errors"], "elapsed_ms": (perf_counter() - start) * 1000})
    return results
