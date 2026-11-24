"""Redacted, bounded UTF-8 JSONL sinks with per-request trace/warning context."""
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime, timezone
import json
import logging
from pathlib import Path
import re
import threading
from uuid import uuid4
from config import settings

_request = ContextVar("unihybrid_request", default=None)
_warnings = ContextVar("unihybrid_log_warnings", default=None)
_lock = threading.RLock()


def redact(value, secrets=()):
    if isinstance(value, dict):
        return {str(k): "[REDACTED]" if re.search(r"api.?key|access.?token|refresh.?token|secret|authorization|password", str(k), re.I)
                else redact(v, secrets) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [redact(item, secrets) for item in value]
    if isinstance(value, str):
        for secret in (settings.api_key, *secrets):
            if secret:
                value = value.replace(secret, "[REDACTED]")
        return re.sub(r"AIza[\w-]{20,}", "[REDACTED]", value)
    return value


@contextmanager
def request_context(request_id):
    token = _request.set(request_id)
    warning_token = _warnings.set([])
    try:
        yield
    finally:
        _request.reset(token)
        _warnings.reset(warning_token)


def current_request_id():
    return _request.get()


def log_warnings():
    return list(_warnings.get() or [])


def _append(path, record):
    line = json.dumps(record, ensure_ascii=False, allow_nan=False) + "\n"
    size = len(line.encode("utf-8"))
    if size > settings.log_max_bytes:
        raise ValueError("Record exceeds configured log cap")
    with _lock:
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and path.stat().st_size + size > settings.log_max_bytes:
            for index in range(settings.log_backups, 0, -1):
                source = path if index == 1 else Path(f"{path}.{index - 1}")
                if source.exists():
                    source.replace(Path(f"{path}.{index}"))
        with path.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(line)


def event(name, **fields):
    """Return a readable operational warning on failure; never interrupt the answer."""
    if name not in ("execution", "llm_call"):
        return None
    if name == "execution":
        evidence = fields.get("evidence", {})
        fields = {key: value for key, value in fields.items() if key not in ("evidence", "answer", "sources")}
        fields["retrieved_chunks"] = [{key: item[key] for key in ("chunk_id", "source_file", "page", "score") if key in item}
                                      for item in evidence.get("docs", [])]
        fields["completion_state"] = "completed_with_warnings" if fields.get("errors") else "completed"
    record = redact({**fields, "schema_version": 1, "event": name,
                     "timestamp": datetime.now(timezone.utc).isoformat(),
                     "request_id": fields.get("request_id") or current_request_id() or str(uuid4())})
    try:
        _append(settings.logs_dir / ("execution.jsonl" if name == "execution" else "prompts.jsonl"), record)
        return None
    except (OSError, ValueError, TypeError):
        warning = "Logging unavailable. Check log directory permissions, disk space, and configured size cap."
        warnings = _warnings.get()
        if warnings is not None and warning not in warnings:
            warnings.append(warning)
        logging.getLogger("unihybrid").warning(warning)
        return warning
