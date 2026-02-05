"""
Unit tests for API endpoints.
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "version" in data
    assert "environment" in data


@patch("api.main.get_rag_system")
def test_query_endpoint_success(mock_get_rag):
    """Test successful query."""
    # Mock RAG system
    mock_rag = MagicMock()
    mock_rag.query.return_value = {
        "question": "Test question",
        "answer": "Test answer",
        "sources": [],
    }
    mock_get_rag.return_value = mock_rag

    response = client.post(
        "/query",
        json={"question": "Test question", "return_sources": True},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["question"] == "Test question"
    assert data["answer"] == "Test answer"


@patch("api.main.get_rag_system")
def test_search_endpoint_success(mock_get_rag):
    """Test successful similarity search."""
    # Mock RAG system
    mock_rag = MagicMock()
    mock_rag.similarity_search.return_value = [
        {"content": "Result 1", "metadata": {}},
        {"content": "Result 2", "metadata": {}},
    ]
    mock_get_rag.return_value = mock_rag

    response = client.post(
        "/search",
        json={"query": "test", "k": 5},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "test"
    assert data["count"] == 2
    assert len(data["results"]) == 2


def test_query_endpoint_validation():
    """Test query endpoint validation."""
    # Empty question
    response = client.post("/query", json={"question": ""})
    assert response.status_code == 422

    # Question too short
    response = client.post("/query", json={"question": "ab"})
    assert response.status_code == 422


def test_search_endpoint_validation():
    """Test search endpoint validation."""
    # Invalid k value
    response = client.post("/search", json={"query": "test", "k": 0})
    assert response.status_code == 422

    # k too large
    response = client.post("/search", json={"query": "test", "k": 100})
    assert response.status_code == 422
