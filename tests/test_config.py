import subprocess
import sys

import pytest
from config import ROOT, load_settings
from src.utils.logger import redact


def test_no_key_import_and_lazy_validation():
    result = load_settings({})
    assert result.db_path == ROOT / "data" / "university.db"
    with pytest.raises(ValueError, match="GEMINI_API_KEY"):
        result.require_api_key()


@pytest.mark.parametrize("name,value", [
    ("TOP_K", "0"), ("TOP_K", "nan"), ("SIM_THRESHOLD", "nan"),
    ("SIM_THRESHOLD", "inf"), ("CHUNK_SIZE", "20"),
    ("CHUNK_OVERLAP", "500"), ("LLM_MAX_RETRIES", "3"),
    ("LLM_TIMEOUT_SECONDS", "16"), ("UPLOAD_LIMIT_MB", "21"),
    ("LLM_TIMEOUT_SECONDS", "5"),
    ("DATA_DIR", " "), ("MODEL_NAME", ""), ("CURRENT_TERM", ""),
])
def test_invalid_configuration(name, value):
    with pytest.raises(ValueError, match=name):
        load_settings({name: value})


def test_key_not_exposed_and_nested_redaction():
    sentinel = "dummy-private-sentinel"
    cfg = load_settings({"GEMINI_API_KEY": sentinel})
    assert sentinel not in repr(cfg)
    assert cfg.require_api_key() == sentinel
    redacted = redact({"error": [sentinel], "api_key": "another"}, [sentinel])
    assert sentinel not in str(redacted)
    assert "another" not in str(redacted)


def test_config_import_does_not_contact_network():
    code = "import socket; socket.socket=lambda *a, **k: (_ for _ in ()).throw(AssertionError('network')); import config"
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
