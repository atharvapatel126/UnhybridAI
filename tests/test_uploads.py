from dataclasses import replace
from pathlib import Path
import pytest
from config import load_settings
from src.ingest import uploads


def test_upload_staging_preserves_name_and_cleans_up(tmp_path, monkeypatch):
    monkeypatch.setattr(uploads, "settings", replace(load_settings({}), data_dir=tmp_path))
    paths = []
    def ingest(path):
        paths.append(Path(path))
        assert Path(path).name == "Demo_Policy.txt"
        assert Path(path).read_bytes() == b"SYNTHETIC policy document content"
        return {"ok": True, "errors": [], "chunks": 1}
    monkeypatch.setattr(uploads, "ingest_file", ingest)
    assert uploads.ingest_upload("Demo_Policy.txt", b"SYNTHETIC policy document content")["ok"]
    assert not paths[0].exists()


@pytest.mark.parametrize("name,content", [("../unsafe.txt", b"data"), ("bad.exe", b"data"),
    ("empty.txt", b""), ("large.txt", b"x" * (20 * 1024 * 1024 + 1))])
def test_invalid_upload_never_ingests(name, content, monkeypatch):
    monkeypatch.setattr(uploads, "ingest_file", lambda *_: pytest.fail("Invalid upload reached indexer"))
    assert not uploads.ingest_upload(name, content)["ok"]
