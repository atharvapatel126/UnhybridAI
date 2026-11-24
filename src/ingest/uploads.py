"""Stage uploaded bytes safely, retaining indexed text but not the original binary."""
from pathlib import Path
import tempfile
from config import settings
from src.ingest.extract import validate_filename
from src.ingest.embed_store import ingest_file


def ingest_upload(name, content):
    if not validate_filename(name):
        return {"ok": False, "errors": ["Use a safe PDF, TXT, or MD filename."], "chunks": 0}
    if not isinstance(content, bytes) or not content:
        return {"ok": False, "errors": ["Upload a nonempty document."], "chunks": 0}
    if len(content) > settings.upload_limit_mb * 1024 * 1024:
        return {"ok": False, "errors": ["File exceeds the 20 MB upload limit."], "chunks": 0}
    try:
        staging = settings.data_dir / "uploads"
        staging.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=staging) as temporary:
            path = Path(temporary) / name
            path.write_bytes(content)
            return ingest_file(path)
    except Exception:
        return {"ok": False, "errors": ["Upload processing unavailable. Check storage and model access."], "chunks": 0}
