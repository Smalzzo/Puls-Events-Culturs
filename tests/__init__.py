"""
Tests package initialization.
Pytest configuration and fixtures.
"""

import os

import pytest


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment variables."""
    os.environ["OPENAGENDA_API_KEY"] = "test_openagenda_key"
    os.environ["OPENAGENDA_AGENDA_UID"] = "test_agenda_uid"
    os.environ["MISTRAL_API_KEY"] = "test_mistral_key"
    os.environ["ENVIRONMENT"] = "development"
    os.environ["DEBUG"] = "true"
    os.environ["LOG_LEVEL"] = "DEBUG"
