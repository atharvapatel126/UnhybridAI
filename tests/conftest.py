"""Tests never write into the active demo log directory."""
from dataclasses import replace
import pytest
from src.utils import logger


@pytest.fixture(autouse=True)
def isolated_logs(tmp_path, monkeypatch):
    monkeypatch.setattr(logger, "settings", replace(logger.settings, logs_dir=tmp_path / "logs"))
