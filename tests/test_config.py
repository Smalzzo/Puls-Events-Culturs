"""
Unit tests for configuration module.
"""

import os
from pathlib import Path

import pytest
from pydantic import ValidationError

from src.config import Settings, settings


def test_settings_from_env(monkeypatch):
    """Test loading settings from environment variables."""
    monkeypatch.setenv("OPENAGENDA_API_KEY", "test_key")
    monkeypatch.setenv("OPENAGENDA_AGENDA_UID", "test_uid")
    monkeypatch.setenv("MISTRAL_API_KEY", "test_mistral_key")

    test_settings = Settings()

    assert settings.openagenda_api_key == "test_key"
    assert settings.openagenda_agenda_uid == "test_uid"
    assert settings.mistral_api_key == "test_mistral_key"


def test_settings_defaults():
    """Test default settings values."""
    # Set required fields
    os.environ["OPENAGENDA_API_KEY"] = "test"
    os.environ["OPENAGENDA_AGENDA_UID"] = "test"
    os.environ["MISTRAL_API_KEY"] = "test"

    settings = Settings()

    assert settings.openagenda_base_url == "https://api.openagenda.com/v2"
    assert settings.openagenda_max_events == 500
    assert settings.mistral_temperature == 0.3
    assert settings.rag_top_k == 5
    assert settings.api_port == 8000


def test_settings_is_production():
    """Test environment detection."""
    os.environ["OPENAGENDA_API_KEY"] = "test"
    os.environ["OPENAGENDA_AGENDA_UID"] = "test"
    os.environ["MISTRAL_API_KEY"] = "test"
    os.environ["ENVIRONMENT"] = "production"

    settings = Settings()

    assert settings.is_production is True
    assert settings.is_development is False


def test_settings_validation():
    """Test settings validation."""
    # Missing required fields should raise error
    with pytest.raises(ValidationError):
        Settings(
            openagenda_api_key="test",
            # Missing openagenda_agenda_uid and mistral_api_key
        )


def test_get_settings_cached():
    """Test that get_settings returns cached instance."""
    settings1 = get_settings()
    settings2 = get_settings()

    assert settings1 is settings2
