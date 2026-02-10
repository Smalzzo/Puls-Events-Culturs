"""
Unit tests for indexer module.
"""

import pytest

from src.chunking import EventChunker

pytestmark = pytest.mark.unit


def test_create_chunks_basic():
    """Test creating chunks from a single event."""
    chunker = EventChunker()

    event = {
        "title_fr": "Concert de Jazz",
        "description_fr": "Un super concert",
        "location_name": "Salle Pleyel",
        "keywords_fr": ["jazz", "musique"],
        "location_city": "Paris",
        "location_region": "Île-de-France",
        "uid": "test_1",
        "firstdate_begin": "2026-01-10T19:00:00",
    }

    documents = chunker.create_chunks([event])

    assert len(documents) >= 2
    assert all(hasattr(doc, "metadata") for doc in documents)
    assert all("event_id" in doc.metadata for doc in documents)
    assert any(doc.metadata.get("chunk_type") == "main" for doc in documents)
    assert any(doc.metadata.get("chunk_type") == "practical" for doc in documents)


def test_create_chunks():
    """Test creating chunks from multiple events."""
    chunker = EventChunker(chunk_size=100, overlap=20)

    events = [
        {
            "uid": "event1",
            "title_fr": "Event 1",
            "description_fr": "Description 1",
            "location_name": "Location 1",
        },
        {
            "uid": "event2",
            "title_fr": "Event 2",
            "description_fr": "Description 2",
            "location_name": "Location 2",
        },
    ]

    documents = chunker.create_chunks(events)

    assert len(documents) > 0
    assert all(hasattr(doc, 'metadata') for doc in documents)
    assert all("event_id" in doc.metadata for doc in documents)


def test_create_chunks_empty():
    """Test creating chunks from empty event list."""
    chunker = EventChunker()
    documents = chunker.create_chunks([])
    assert documents == []

