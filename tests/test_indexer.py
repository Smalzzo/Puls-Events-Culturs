"""
Unit tests for indexer module.
"""

import pytest

from src.chunking import EventChunker


def test_event_to_text():
    """Test event to text conversion."""
    chunker = EventChunker()

    event = {
        "title_fr": "Concert de Jazz",
        "description_fr": "Un super concert",
        "location_name": "Salle Pleyel",
        "keywords_fr": ["jazz", "musique"],
        "uid": "test_1"
    }

    text = chunker.event_to_text(event)

    assert "Concert de Jazz" in text
    assert "Un super concert" in text
    assert "Salle Pleyel" in text
    assert "jazz" in text


def test_event_to_text_empty():
    """Test event to text with empty event."""
    chunker = EventChunker()
    event = {}
    text = chunker.event_to_text(event)
    assert text == ""


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

