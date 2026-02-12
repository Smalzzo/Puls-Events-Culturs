"""
Unit tests for chunking utilities.
"""

import pytest

from src.chunking import EventChunker

pytestmark = pytest.mark.unit


def test_normalize_date_valid():
    chunker = EventChunker()
    result = chunker.normalize_date("2026-01-10T19:00:00")
    assert "10/01/2026" in result
    assert "19:00" in result


def test_normalize_date_invalid_passthrough():
    chunker = EventChunker()
    value = "not-a-date"
    assert chunker.normalize_date(value) == value


def test_create_chunks_long_description_splits():
    chunker = EventChunker(chunk_size=100, overlap=10)
    long_desc = "word " * 120  # > 400 chars
    event = {
        "uid": "evt_1",
        "title_fr": "Event",
        "description_fr": long_desc,
        "location_city": "Paris",
        "location_region": "IDF",
        "firstdate_begin": "2026-01-10T19:00:00",
    }

    docs = chunker.create_chunks([event])
    chunk_types = {d.metadata.get("chunk_type") for d in docs}

    assert "main" in chunk_types
    assert "practical" in chunk_types
    assert "description" in chunk_types
    assert all(d.metadata.get("event_id") == "evt_1" for d in docs)


def test_split_text_overlap():
    chunker = EventChunker()
    text = "a " * 60
    chunks = chunker._split_text(text, size=50, overlap=5)
    assert len(chunks) > 1
