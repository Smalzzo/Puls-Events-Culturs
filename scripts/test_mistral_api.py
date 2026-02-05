"""
Script pour tester la connexion à l'API Mistral.
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config import settings
from langchain_mistralai import ChatMistralAI, MistralAIEmbeddings


def test_chat_api():
    """Test de l'API Chat Mistral."""
    print("=" * 60)
    print("TEST 1: API Chat Mistral")
    print("=" * 60)
    print()
    
    try:
        print(f"Modèle : {settings.mistral_model_name}")
        print(f"API Key : {settings.mistral_api_key[:10]}...")
        print()
        
        llm = ChatMistralAI(
            model=settings.mistral_model_name,
            api_key=settings.mistral_api_key,
            temperature=0.3,
            timeout=30,
        )
        
        print("Envoi d'une requête test...")
        response = llm.invoke("Dis bonjour en une phrase")
        
        print("✓ Succès !")
        print(f"Réponse : {response.content}")
        print()
        return True
        
    except Exception as e:
        print(f"✗ Échec : {e}")
        print()
        return False


def test_embeddings_api():
    """Test de l'API Embeddings Mistral."""
    print("=" * 60)
    print("TEST 2: API Embeddings Mistral")
    print("=" * 60)
    print()
    
    try:
        print(f"Modèle : {settings.embedding_model_name}")
        print(f"API Key : {settings.mistral_api_key[:10]}...")
        print()
        
        embeddings = MistralAIEmbeddings(
            model=settings.embedding_model_name,
            api_key=settings.mistral_api_key,
        )
        
        print("Génération d'embeddings pour un texte test...")
        result = embeddings.embed_query("Ceci est un test")
        
        print("✓ Succès !")
        print(f"Dimension du vecteur : {len(result)}")
        print(f"Premiers éléments : {result[:5]}")
        print()
        return True
        
    except Exception as e:
        print(f"✗ Échec : {e}")
        print()
        return False


def test_multiple_requests():
    """Test de requêtes multiples pour vérifier le rate limit."""
    print("=" * 60)
    print("TEST 3: Requêtes multiples (Rate Limit)")
    print("=" * 60)
    print()
    
    try:
        llm = ChatMistralAI(
            model=settings.mistral_model_name,
            api_key=settings.mistral_api_key,
            temperature=0.3,
            timeout=30,
        )
        
        questions = [
            "Question 1: Bonjour",
            "Question 2: Comment vas-tu?",
            "Question 3: Quelle heure est-il?",
        ]
        
        for i, question in enumerate(questions, 1):
            print(f"Requête {i}/3: {question}")
            response = llm.invoke(question)
            print(f"  ✓ Réponse : {response.content[:50]}...")
            print()
        
        print("✓ Toutes les requêtes ont réussi")
        print()
        return True
        
    except Exception as e:
        print(f"✗ Échec : {e}")
        print()
        return False


def main():
    """Lance tous les tests."""
    print()
    print("=" * 60)
    print("TESTS DE L'API MISTRAL")
    print("=" * 60)
    print()
    
    results = []
    
    # Test 1: Chat API
    results.append(("Chat API", test_chat_api()))
    
    # Test 2: Embeddings API
    results.append(("Embeddings API", test_embeddings_api()))
    
    # Test 3: Requêtes multiples
    results.append(("Requêtes multiples", test_multiple_requests()))
    
    # Résumé
    print("=" * 60)
    print("RÉSUMÉ DES TESTS")
    print("=" * 60)
    print()
    
    for test_name, success in results:
        status = "✓ SUCCÈS" if success else "✗ ÉCHEC"
        print(f"  {test_name:25s} : {status}")
    
    print()
    
    all_success = all(result[1] for result in results)
    
    if all_success:
        print("=" * 60)
        print("Tous les tests ont réussi ! L'API Mistral fonctionne.")
        print("=" * 60)
    else:
        print("=" * 60)
        print("Certains tests ont échoué. Vérifiez :")
        print("  - Votre clé API Mistral")
        print("  - Votre connexion Internet")
        print("  - Les quotas de votre compte Mistral")
        print("=" * 60)


if __name__ == "__main__":
    main()