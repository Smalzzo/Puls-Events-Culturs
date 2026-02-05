"""
Module d'évaluation RAGAS pour le système RAG.
"""

from typing import Any, Optional
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)
from langchain_mistralai import ChatMistralAI
from langchain_community.embeddings import HuggingFaceEmbeddings

try:
    from langchain_mistralai import MistralAIEmbeddings
    MISTRAL_AVAILABLE = True
except ImportError:
    MISTRAL_AVAILABLE = False

from src.rag import get_rag_system
from src.config import settings
from src.logger import get_logger

logger = get_logger(__name__)


class RAGASEvaluator:
    """Évalue la qualité du système RAG avec RAGAS."""

    def __init__(self, use_mistral_embeddings: Optional[bool] = None):
        """
        Initialise l'évaluateur RAGAS.
        
        Args:
            use_mistral_embeddings: Si True, utilise Mistral pour embeddings, sinon HuggingFace
        """
        self.rag_system = get_rag_system()
        self.use_mistral_embeddings = use_mistral_embeddings if use_mistral_embeddings is not None else settings.use_mistral_embeddings
        
        self.evaluator_llm = ChatMistralAI(
            model=settings.mistral_evaluator_model,
            api_key=settings.mistral_api_key,
            temperature=0,
        )
        
        if self.use_mistral_embeddings:
            if not MISTRAL_AVAILABLE:
                logger.error("Mistral demandé mais langchain-mistralai n'est pas installé")
                raise ImportError("langchain-mistralai n'est pas installé")
            
            logger.info(f"RAGAS: Utilisation de Mistral AI Embeddings: {settings.mistral_embedding_model}")
            self.embeddings = MistralAIEmbeddings(
                model=settings.mistral_embedding_model,
                api_key=settings.mistral_api_key,
            )
        else:
            logger.info(f"RAGAS: Utilisation de HuggingFace Embeddings: {settings.huggingface_embedding_model}")
            self.embeddings = HuggingFaceEmbeddings(
                model_name=settings.huggingface_embedding_model,
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True},
            )
        
        self.metrics = [
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall,
        ]
        
        logger.info("Évaluateur RAGAS initialisé")

    def create_evaluation_dataset(
        self, test_questions: list[dict[str, str]]
    ) -> Dataset:
        """
        Crée un dataset d'évaluation à partir de questions de test.

        Args:
            test_questions: Liste de dicts avec 'question' et 'ground_truth'

        Returns:
            Dataset RAGAS
        """
        logger.info(f"Création du dataset d'évaluation avec {len(test_questions)} questions")

        data = {
            "question": [],
            "answer": [],
            "contexts": [],
            "ground_truth": [],
        }

        for item in test_questions:
            question = item["question"]
            ground_truth = item.get("ground_truth", "")

            # Génération de la réponse via le RAG
            response = self.rag_system.query(question=question, return_sources=True)

            # Extraction des contextes depuis les sources
            contexts = []
            if "sources" in response:
                for source in response["sources"]:
                    contexts.append(source.get('content', ''))

            # Ajout au dataset
            data["question"].append(question)
            data["answer"].append(response["answer"])
            data["contexts"].append(contexts)
            data["ground_truth"].append(ground_truth)

        return Dataset.from_dict(data)

    def evaluate(self, test_questions: list[dict[str, str]]) -> dict[str, Any]:
        """
        Évalue le système RAG avec RAGAS.

        Args:
            test_questions: Liste de questions de test avec réponses attendues

        Returns:
            Résultats d'évaluation
        """
        logger.info("Démarrage de l'évaluation RAGAS...")

        dataset = self.create_evaluation_dataset(test_questions)

        results = evaluate(
            dataset, 
            metrics=self.metrics,
            llm=self.evaluator_llm,
            embeddings=self.embeddings,
        )

        logger.info("Évaluation RAGAS terminée")
        logger.info(f"Résultats : {results}")

        return results

    def evaluate_from_file(self, test_file_path: str) -> dict[str, Any]:
        """
        Évalue à partir d'un fichier JSON de questions.

        Args:
            test_file_path: Chemin vers le fichier JSON

        Returns:
            Résultats d'évaluation
        """
        import json
        from pathlib import Path

        logger.info(f"Chargement des questions depuis {test_file_path}")

        test_path = Path(test_file_path)
        if not test_path.exists():
            raise FileNotFoundError(f"Fichier de test introuvable : {test_file_path}")

        with open(test_path, "r", encoding="utf-8") as f:
            test_questions = json.load(f)

        return self.evaluate(test_questions)


def get_ragas_evaluator() -> RAGASEvaluator:
    """Récupère une instance de l'évaluateur RAGAS."""
    return RAGASEvaluator()