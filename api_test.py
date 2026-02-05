"""
Script de test fonctionnel pour l'API RAG Événements Culturels.
"""

import requests
import json
from typing import Dict, Any
from datetime import datetime


# Configuration
API_URL = "http://localhost:8000"
COLORS = {
    "green": "\033[92m",
    "red": "\033[91m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "reset": "\033[0m"
}


def print_colored(message: str, color: str = "reset") -> None:
    """Affiche un message coloré."""
    print(f"{COLORS.get(color, '')}{message}{COLORS['reset']}")


def print_section(title: str) -> None:
    """Affiche un titre de section."""
    print("\n" + "=" * 80)
    print_colored(f"  {title}", "blue")
    print("=" * 80)


def test_health() -> bool:
    """Teste le endpoint /health."""
    print_section("TEST 1: Health Check")
    
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print_colored("✓ Health check réussi", "green")
            print(f"  Status: {data['status']}")
            print(f"  Version: {data['version']}")
            print(f"  Environment: {data['environment']}")
            print(f"  Index loaded: {data['index_loaded']}")
            return data['index_loaded']
        else:
            print_colored(f"✗ Health check échoué: {response.status_code}", "red")
            return False
            
    except Exception as e:
        print_colored(f"✗ Erreur de connexion: {e}", "red")
        return False


def test_ask(question: str) -> Dict[str, Any]:
    """Teste le endpoint /ask avec une question."""
    try:
        response = requests.post(
            f"{API_URL}/ask",
            json={"question": question},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print_colored(f"✓ Question: {question}", "green")
            print(f"  Réponse: {data['answer']}")
            print(f"  Nombre de sources: {len(data.get('sources', []))}")
            
            # Afficher les sources si présentes
            if data.get('sources'):
                print("  Sources:")
                for i, source in enumerate(data['sources'][:3], 1):
                    print(f"    {i}. {source.get('title', 'N/A')} - {source.get('location', 'N/A')}")
            
            return data
        else:
            print_colored(f"✗ Erreur {response.status_code}: {response.text}", "red")
            return {}
            
    except Exception as e:
        print_colored(f"✗ Erreur: {e}", "red")
        return {}


def test_multiple_questions() -> None:
    """Teste plusieurs questions variées."""
    print_section("TEST 2: Questions variées")
    
    questions = [
        "Quels spectacles sont disponibles à Paris ce weekend?",
        "Y a-t-il des expositions à Versailles?",
        "Je cherche un concert de jazz",
        "Événements culturels gratuits en Île-de-France",
        "Y a-t-il un festival en septembre?",
    ]
    
    successful = 0
    for i, question in enumerate(questions, 1):
        print(f"\n--- Question {i}/{len(questions)} ---")
        result = test_ask(question)
        if result:
            successful += 1
    
    print(f"\n{successful}/{len(questions)} questions réussies")


def test_edge_cases() -> None:
    """Teste des cas limites."""
    print_section("TEST 3: Cas limites")
    
    edge_cases = [
        ("Question très courte", "Paris?"),
        ("Question hors contexte", "Y a-t-il un spectacle à Lyon?"),
        ("Question vague", "événement"),
        ("Question longue", "Je cherche un événement culturel gratuit pour toute la famille, de préférence un spectacle ou une exposition, qui se déroule à Paris ou dans les environs proches, idéalement le weekend prochain ou dans le mois à venir."),
    ]
    
    for label, question in edge_cases:
        print(f"\n--- {label} ---")
        test_ask(question)


def test_evaluate() -> bool:
    """Teste le endpoint /evaluate."""
    print_section("TEST 4: Évaluation RAGAS")
    
    try:
        print("Lancement de l'évaluation RAGAS (peut prendre plusieurs minutes)...")
        response = requests.post(
            f"{API_URL}/evaluate",
            json={"test_file_path": "data/test/ragas_questions_mini.json"},
            timeout=300
        )
        
        if response.status_code == 200:
            data = response.json()
            print_colored("✓ Évaluation réussie", "green")
            print("\nMétriques RAGAS:")
            for metric, score in data['metrics'].items():
                color = "green" if score > 0.6 else "yellow" if score > 0.4 else "red"
                print_colored(f"  {metric}: {score:.3f}", color)
            return True
        else:
            print_colored(f"✗ Évaluation échouée: {response.status_code}", "red")
            print(response.text)
            return False
            
    except Exception as e:
        print_colored(f"✗ Erreur: {e}", "red")
        return False


def test_rebuild_sample() -> bool:
    """Teste le endpoint /rebuild avec un événement exemple."""
    print_section("TEST 5: Ajout d'événement (rebuild)")
    
    sample_event = {
        "title_fr": "Concert de Jazz Test",
        "description_fr": "Un concert de jazz exceptionnel pour tester l'API",
        "location_name": "Salle de Test",
        "location_city": "Paris",
        "location_region": "Île-de-France",
        "firstdate_begin": "2026-03-15T20:00:00",
        "lastdate_end": "2026-03-15T22:00:00",
        "event_id": "test_12345"
    }
    
    try:
        print("Ajout d'un événement de test à l'index...")
        response = requests.post(
            f"{API_URL}/rebuild",
            json={"events": [sample_event]},
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print_colored("✓ Événement ajouté", "green")
            print(f"  Events processed: {data['events_processed']}")
            print(f"  Chunks created: {data['chunks_created']}")
            print(f"  Message: {data['message']}")
            
            # Vérifier que l'événement est bien retrouvable
            print("\nVérification de la récupération...")
            test_ask("Concert de Jazz Test")
            return True
        else:
            print_colored(f"✗ Ajout échoué: {response.status_code}", "red")
            print(response.text)
            return False
            
    except Exception as e:
        print_colored(f"✗ Erreur: {e}", "red")
        return False


def run_all_tests() -> None:
    """Lance tous les tests."""
    print_colored("\n" + "=" * 80, "blue")
    print_colored("  TESTS FONCTIONNELS API RAG ÉVÉNEMENTS CULTURELS", "blue")
    print_colored("=" * 80 + "\n", "blue")
    
    start_time = datetime.now()
    
    # Test 1: Health check
    index_loaded = test_health()
    if not index_loaded:
        print_colored("\n⚠ L'index n'est pas chargé. Certains tests vont échouer.", "yellow")
        return
    
    # Test 2: Questions variées
    test_multiple_questions()
    
    # Test 3: Cas limites
    test_edge_cases()
    
    # Test 4: Évaluation (optionnel - commentez si trop long)
    print_colored("\n⚠ Test d'évaluation RAGAS désactivé (décommentez pour l'activer)", "yellow")
    # test_evaluate()
    
    # Test 5: Rebuild (optionnel - modifie l'index)
    print_colored("\n⚠ Test rebuild désactivé (décommentez pour l'activer)", "yellow")
    # test_rebuild_sample()
    
    # Résumé
    duration = (datetime.now() - start_time).total_seconds()
    print_section("RÉSUMÉ")
    print(f"Durée totale: {duration:.2f}s")
    print_colored("\n✓ Tests terminés", "green")


if __name__ == "__main__":
    run_all_tests()
