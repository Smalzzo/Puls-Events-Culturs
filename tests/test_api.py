"""
Unit tests for API endpoints.
"""

from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_root_endpoint():
    """Root endpoint not defined; ensure 404."""
    response = client.get("/")
    assert response.status_code == 404


def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "version" in data
    assert "environment" in data


@patch("api.main.get_rag_system")
def test_ask_endpoint_success(mock_get_rag):
    """Test successful /ask."""
    # Mock RAG system
    mock_rag = MagicMock()
    mock_rag.query.return_value = {
        "question": "Test question",
        "answer": "Test answer",
        "sources": [],
    }
    mock_get_rag.return_value = mock_rag

    response = client.post(
        "/ask",
        json={"question": "Test question"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["question"] == "Test question"
    assert data["answer"] == "Test answer"


def test_ask_endpoint_validation():
    """Test /ask validation."""
    # Empty question
    response = client.post("/ask", json={"question": ""})
    assert response.status_code == 422

    # Question too short
    response = client.post("/ask", json={"question": "ab"})
    assert response.status_code == 422
