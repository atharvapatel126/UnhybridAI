"""Portable CSV/JSON artifacts, metadata hashes, and explicit N/A values."""
import csv
import hashlib
from importlib import metadata
import json
from pathlib import Path
import platform
from datetime import datetime, timezone
from config import ROOT, settings
from src.ingest.embed_store import MODEL_ID, MODEL_REVISION


def write_csv(path, records):
    if not records:
        return
    with Path(path).open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(records[0]))
        writer.writeheader()
        for record in records:
            writer.writerow({key: json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list))
                             else "N/A" if value is None else value for key, value in record.items()})


def write_summary(directory, summary):
    (directory / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    flat = []
    def flatten(prefix, value):
        if isinstance(value, dict):
            for key, item in value.items():
                flatten(f"{prefix}.{key}" if prefix else key, item)
        else:
            flat.append({"metric": prefix, "value": value})
    flatten("", summary)
    write_csv(directory / "metrics.csv", flat)


def run_metadata(dataset, mode, image_id):
    digest = hashlib.sha256()
    files = [ROOT / "config.py", ROOT / "app.py", *ROOT.glob("src/**/*.py"), *ROOT.glob("scripts/**/*.py")]
    for path in sorted(files):
        digest.update(str(path.relative_to(ROOT)).replace("\\", "/").encode())
        digest.update(path.read_bytes())
    versions = {package: metadata.version(package) for package in
                ("streamlit", "google-genai", "sentence-transformers", "chromadb", "pymupdf", "torch")}
    return {"timestamp_utc": datetime.now(timezone.utc).isoformat(), "mode": mode,
            "model": settings.model_name, "embedding_model": MODEL_ID, "embedding_revision": MODEL_REVISION,
            "dataset_sha256": hashlib.sha256(dataset.read_bytes()).hexdigest(), "source_sha256": digest.hexdigest(),
            "db_sha256": hashlib.sha256(settings.db_path.read_bytes()).hexdigest() if settings.db_path.exists() else None,
            "manifest_sha256": hashlib.sha256((settings.chroma_dir / "documents.json").read_bytes()).hexdigest()
            if (settings.chroma_dir / "documents.json").exists() else None,
            "image_id": image_id, "platform": platform.platform(), "python": platform.python_version(),
            "dependencies": versions, "top_k": settings.top_k, "similarity_threshold": settings.sim_threshold,
            "chunk_size":settings.chunk_size, "chunk_overlap":settings.chunk_overlap, "current_term":settings.current_term,
            "llm_timeout_seconds":settings.timeout_seconds, "llm_max_retries":settings.max_retries,
            "latency_method": "outer monotonic wall clock; p=(n-1)*q linear interpolation; pauses excluded",
            "model_warmup": "ingestion probe runs first; see measured embedding-cache flag; no cold-download latency claim",
            "human_review": "pending; structural citation validity is not source attribution or faithfulness"}
