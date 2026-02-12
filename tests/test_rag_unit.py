"""
Unit tests for RAG system error paths.
"""

import pytest

from src.rag import RAGSystem

pytestmark = pytest.mark.unit


def test_load_index_missing_raises(tmp_path):
    rag = RAGSystem(index_path=str(tmp_path / "missing"))
    with pytest.raises(FileNotFoundError):
        rag.load_index()


def test_query_without_chain_raises(tmp_path):
    rag = RAGSystem(index_path=str(tmp_path / "missing"))
    with pytest.raises(ValueError):
        rag.query("question")


def test_setup_qa_chain_without_vectorstore_raises(tmp_path):
    rag = RAGSystem(index_path=str(tmp_path / "missing"))
    with pytest.raises(ValueError):
        rag.setup_qa_chain()
