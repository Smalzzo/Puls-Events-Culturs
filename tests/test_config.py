"""
Unit tests for configuration module.
"""

import os


from src.config import Settings


def test_settings_from_env(monkeypatch):
    """Test loading settings from environment variables."""
    monkeypatch.setenv("OPENAGENDA_API_KEY", "test_key")
    monkeypatch.setenv("OPENAGENDA_AGENDA_UID", "test_uid")
    monkeypatch.setenv("MISTRAL_API_KEY", "test_mistral_key")

    test_settings = Settings()

    assert test_settings.openagenda_api_key == "test_key"
    assert test_settings.openagenda_agenda_uid == "test_uid"
    assert test_settings.mistral_api_key == "test_mistral_key"


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
    assert settings.rag_top_k == 10
    assert settings.api_port == 8000


def test_settings_environment_value():
    """Test environment value is read from ENVIRONMENT."""
    os.environ["ENVIRONMENT"] = "production"
    settings = Settings()
    assert settings.environment == "production"
