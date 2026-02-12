"""
Unit tests for logger setup.
"""

import logging

import pytest

from src.config import settings
from src.logger import setup_logging

pytestmark = pytest.mark.unit


def test_setup_logging_writes_file_handler(tmp_path, monkeypatch):
    log_path = tmp_path / "app.log"

    monkeypatch.setattr(settings, "log_file", str(log_path), raising=False)
    monkeypatch.setattr(settings, "log_level", "INFO", raising=False)
    monkeypatch.setattr(
        settings,
        "log_format",
        "%(levelname)s - %(message)s",
        raising=False,
    )

    setup_logging()

    root_logger = logging.getLogger()
    file_handlers = [
        h for h in root_logger.handlers if isinstance(h, logging.FileHandler)
    ]
    assert file_handlers
    assert log_path.exists()
