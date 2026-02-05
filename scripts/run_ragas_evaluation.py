"""
Script pour lancer l'évaluation RAGAS manuellement.
"""

import sys
from pathlib import Path

# Ajouter le répertoire parent au path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.ragas_eval import get_ragas_evaluator
from src.rag import get_rag_system
from src.logger import get_logger

logger = get_logger(__name__)


def main():
    """Lance l'évaluation RAGAS manuellement."""
    
    print("=" * 60)
    print("ÉVALUATION RAGAS DU SYSTÈME RAG")
    print("=" * 60)
    print()
    
    # Chemin vers le fichier de questions de test
    test_file = "data/test/ragas_questions.json"
    
    print(f"Fichier de test : {test_file}")
    print()
    
    # Vérifier que le fichier existe
    if not Path(test_file).exists():
        print(f"ERREUR : Le fichier {test_file} n'existe pas")
        print("Créez d'abord le fichier avec des questions de test")
        return
    
    try:
        # Initialiser le système RAG
        print("Initialisation du système RAG...")
        rag_system = get_rag_system()
        
        # Charger l'index FAISS
        print("Chargement de l'index FAISS...")
        rag_system.load_index()
        
        # Initialiser le LLM
        print("Initialisation du LLM Mistral...")
        rag_system.initialize_llm()
        
        # Configurer la chaîne Q&A
        print("Configuration de la chaîne Q&A...")
        rag_system.setup_qa_chain()
        
        print("Système RAG prêt")
        print()
        
        # Créer l'évaluateur
        print("Initialisation de l'évaluateur RAGAS...")
        evaluator = get_ragas_evaluator()
        print("Évaluateur initialisé")
        print()
        
        # Lancer l'évaluation
        print("Démarrage de l'évaluation (cela peut prendre plusieurs minutes)...")
        print()
        results = evaluator.evaluate_from_file(test_file)
        
        # Afficher les résultats
        print()
        print("=" * 60)
        print("RÉSULTATS DE L'ÉVALUATION")
        print("=" * 60)
        print()
        
        for metric, score in results.items():
            print(f"  {metric:25s} : {score:.4f}")
        
        print()
        print("=" * 60)
        print("Évaluation terminée avec succès")
        print("=" * 60)
        
    except FileNotFoundError as e:
        print()
        print("=" * 60)
        print(f"ERREUR : {e}")
        print("=" * 60)
        print()
        print("Vous devez d'abord construire l'index FAISS.")
        print("Utilisez l'une de ces méthodes :")
        print("  1. Via l'API : POST /rebuild avec des événements")
        print("  2. Via un script : python scripts/build_index.py")
        
    except Exception as e:
        print()
        print("=" * 60)
        print(f"ERREUR : {e}")
        print("=" * 60)
        logger.error(f"Erreur lors de l'évaluation : {e}", exc_info=True)


if __name__ == "__main__":
    main()