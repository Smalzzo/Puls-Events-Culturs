"""
Configuration pytest et fixtures communes pour tous les tests.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock

# Ajouter le répertoire racine au PYTHONPATH
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))


@pytest.fixture
def sample_event():
    """Fixture pour un événement de test standard."""
    return {
        "uid": "test_event_123",
        "title_fr": "Festival de Test",
        "description_fr": "Une description complète de l'événement de test",
        "location_name": "Salle de Test",
        "location_city": "Paris",
        "location_region": "Île-de-France",
        "firstdate_begin": "2025-06-15T20:00:00",
        "lastdate_end": "2025-06-15T23:00:00",
        "keywords_fr": ["test", "festival"]
    }


@pytest.fixture
def sample_events_list():
    """Fixture pour une liste d'événements de test."""
    return [
        {
            "uid": f"event_{i}",
            "title_fr": f"Event {i}",
            "description_fr": f"Description for event {i}",
            "location_city": "Paris",
            "location_region": "Île-de-France"
        }
        for i in range(5)
    ]


@pytest.fixture
def sample_test_questions():
    """Fixture pour des questions de test RAGAS."""
    return [
        {
            "question": "Quels spectacles sont disponibles à Paris?",
            "ground_truth": "Il y a plusieurs spectacles à Paris incluant des concerts et des expositions."
        },
        {
            "question": "Y a-t-il des événements gratuits?",
            "ground_truth": "Oui, il existe plusieurs événements culturels gratuits en Île-de-France."
        }
    ]


@pytest.fixture
def mock_rag_system():
    """Fixture pour un système RAG mocké."""
    mock_rag = MagicMock()
    mock_rag.query.return_value = {
        "question": "Test question",
        "answer": "Test answer",
        "sources": [
            {
                "content": "Source content 1",
                "metadata": {"event_id": "1"}
            }
        ]
    }
    mock_rag.similarity_search.return_value = [
        {"content": "Result 1", "metadata": {"event_id": "1"}},
        {"content": "Result 2", "metadata": {"event_id": "2"}}
    ]
    return mock_rag


@pytest.fixture
def mock_embeddings():
    """Fixture pour des embeddings mockés."""
    mock = MagicMock()
    mock.embed_documents.return_value = [[0.1, 0.2, 0.3] for _ in range(10)]
    mock.embed_query.return_value = [0.1, 0.2, 0.3]
    return mock


@pytest.fixture
def mock_vectorstore():
    """Fixture pour un vectorstore mocké."""
    from langchain_core.documents import Document
    
    mock = MagicMock()
    mock.similarity_search.return_value = [
        Document(page_content="Result 1", metadata={"event_id": "1"}),
        Document(page_content="Result 2", metadata={"event_id": "2"})
    ]
    mock.similarity_search_with_score.return_value = [
        (Document(page_content="Result 1", metadata={"event_id": "1"}), 0.95),
        (Document(page_content="Result 2", metadata={"event_id": "2"}), 0.85)
    ]
    return mock


@pytest.fixture
def tmp_index_path(tmp_path):
    """Fixture pour un chemin d'index temporaire."""
    index_dir = tmp_path / "test_index"
    index_dir.mkdir(exist_ok=True)
    return index_dir


@pytest.fixture
def sample_ragas_results():
    """Fixture pour des résultats RAGAS de test."""
    return {
        "faithfulness": 0.85,
        "answer_relevancy": 0.90,
        "context_precision": 0.80,
        "context_recall": 0.75
    }


@pytest.fixture
def mock_settings():
    """Fixture pour des paramètres mockés."""
    from unittest.mock import MagicMock
    
    settings = MagicMock()
    settings.use_mistral_embeddings = False
    settings.huggingface_embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
    settings.mistral_model_name = "mistral-small-latest"
    settings.mistral_api_key = "test_api_key"
    settings.mistral_embedding_model = "mistral-embed"
    settings.mistral_evaluator_model = "mistral-small-latest"
    settings.faiss_index_path = "test_index"
    settings.chunk_size = 300
    settings.chunk_overlap = 50
    return settings


# Hooks pytest pour l'affichage

def pytest_configure(config):
    """Configuration globale pytest."""
    config.addinivalue_line(
        "markers", "unit: Tests unitaires rapides"
    )
    config.addinivalue_line(
        "markers", "integration: Tests d'intégration"
    )
   


def pytest_collection_modifyitems(config, items):
    """Modifie la collection de tests pour ajouter des marqueurs automatiques."""
    for item in items:
        # Ajouter le marqueur 'unit' par défaut si aucun marqueur n'est présent
        if not any(mark.name in ["unit", "integration", "performance", "evaluation"] 
                   for mark in item.iter_markers()):
            item.add_marker(pytest.mark.unit)
        


def pytest_report_header(config):
    """En-tête personnalisé pour les rapports de test."""
    return [
        "Puls Events Culturs RAG - Test Suite",
        "=" * 80
    ]


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Résumé personnalisé à la fin des tests."""
    if exitstatus == 0:
        terminalreporter.write_line(
            "\n✓ Tous les tests ont réussi!", 
            green=True, 
            bold=True
        )
    else:
        terminalreporter.write_line(
            f"\n✗ Tests échoués (code de sortie: {exitstatus})", 
            red=True, 
            bold=True
        )
