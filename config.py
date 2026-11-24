"""Validated configuration; importing this module never contacts external services."""
from dataclasses import dataclass, field
import math
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent


def _number(env, name, default, kind, minimum, maximum):
    try:
        value = kind(env.get(name, default))
        if not math.isfinite(value) or not minimum <= value <= maximum:
            raise ValueError
        return value
    except (ValueError, TypeError):
        raise ValueError(f"{name} must be between {minimum} and {maximum}.") from None


def _path(env, name, default):
    value = env.get(name, str(default)).strip()
    if not value:
        raise ValueError(f"{name} must be a non-empty path.")
    result = Path(value).expanduser()
    return result if result.is_absolute() else ROOT / result


@dataclass(frozen=True)
class Settings:
    api_key: str = field(repr=False)
    model_name: str
    data_dir: Path
    db_path: Path
    chroma_dir: Path
    raw_docs_dir: Path
    logs_dir: Path
    model_cache: Path
    top_k: int
    sim_threshold: float
    chunk_size: int
    chunk_overlap: int
    upload_limit_mb: int
    timeout_seconds: float
    max_retries: int
    backoff_seconds: float
    current_term: str
    log_max_bytes: int
    log_backups: int

    def require_api_key(self):
        if not self.api_key:
            raise ValueError("Set GEMINI_API_KEY in your local .env to use Gemini.")
        return self.api_key


def load_settings(environ=None):
    if environ is None:
        load_dotenv(ROOT / ".env", override=False)
        environ = os.environ
    env = environ
    data = _path(env, "DATA_DIR", ROOT / "data")
    size = _number(env, "CHUNK_SIZE", 500, int, 30, 10000)
    overlap = _number(env, "CHUNK_OVERLAP", 80, int, 0, size - 1)
    model = env.get("MODEL_NAME", "gemini-3.5-flash-lite").strip()
    term = env.get("CURRENT_TERM", "2026-FALL").strip()
    if not model or not term:
        raise ValueError("MODEL_NAME and CURRENT_TERM must be non-empty.")
    return Settings(
        api_key=env.get("GEMINI_API_KEY", "").strip(), model_name=model,
        data_dir=data, db_path=_path(env, "DB_PATH", data / "university.db"),
        chroma_dir=_path(env, "CHROMA_DIR", data / "chroma"),
        raw_docs_dir=_path(env, "RAW_DOCS_DIR", ROOT / "data" / "raw_docs"),
        logs_dir=_path(env, "LOGS_DIR", ROOT / "logs"),
        model_cache=_path(env, "MODEL_CACHE", ROOT / ".cache" / "models"),
        top_k=_number(env, "TOP_K", 5, int, 1, 50),
        sim_threshold=_number(env, "SIM_THRESHOLD", .35, float, -1, 1),
        chunk_size=size, chunk_overlap=overlap,
        upload_limit_mb=_number(env, "UPLOAD_LIMIT_MB", 20, int, 1, 20),
        timeout_seconds=_number(env, "LLM_TIMEOUT_SECONDS", 15, float, 10, 15),
        max_retries=_number(env, "LLM_MAX_RETRIES", 2, int, 0, 2),
        backoff_seconds=_number(env, "LLM_BACKOFF_SECONDS", 1, float, 0, 5),
        current_term=term,
        log_max_bytes=_number(env, "LOG_MAX_BYTES", 5_000_000, int, 1024, 100_000_000),
        log_backups=_number(env, "LOG_BACKUPS", 3, int, 1, 10),
    )


settings = load_settings()
