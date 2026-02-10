"""
Functional API tests using a live server (HTTP).
"""

import os

import pytest
import requests


API_URL = os.getenv("API_URL", "http://localhost:8000").rstrip("/")

pytestmark = pytest.mark.functional


def _get_health():
    return requests.get(f"{API_URL}/health", timeout=5)


@pytest.fixture(scope="session")
def server_health():
    """Return health payload or skip if API is not reachable."""
    try:
        resp = _get_health()
    except Exception:
        pytest.skip("API server not reachable; functional tests skipped.")
    if resp.status_code != 200:
        pytest.skip(f"API health failed: {resp.status_code}")
    return resp.json()


@pytest.mark.functional
@pytest.mark.api
def test_health_endpoint(server_health):
    assert "status" in server_health
    assert "version" in server_health
    assert "environment" in server_health
    assert "index_loaded" in server_health


@pytest.mark.functional
@pytest.mark.api
def test_docs_endpoint(server_health):
    resp = requests.get(f"{API_URL}/docs", timeout=5)
    assert resp.status_code == 200


@pytest.mark.functional
@pytest.mark.api
def test_ask_endpoint(server_health):
    if not server_health.get("index_loaded"):
        pytest.skip("Index not loaded; /ask test skipped.")

    resp = requests.post(
        f"{API_URL}/ask",
        json={"question": "Quels sont les concerts de jazz à Paris ?"},
        timeout=30,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "answer" in data
