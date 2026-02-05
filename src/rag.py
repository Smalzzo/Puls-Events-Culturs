"""
Système RAG pour la recherche d'événements culturels.
"""

from pathlib import Path
from typing import Any, Optional

from pydantic import SecretStr
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_mistralai import ChatMistralAI

# Import optionnel de Mistral embeddings
try:
    from langchain_mistralai import MistralAIEmbeddings
    MISTRAL_AVAILABLE = True
except ImportError:
    MISTRAL_AVAILABLE = False

from src.config import settings
from src.logger import get_logger
from src.prompts import ANTI_HALLUCINATION_PROMPT

# Import optionnel du reranker
try:
    from sentence_transformers import CrossEncoder
    RERANKER_AVAILABLE = True
except ImportError:
    RERANKER_AVAILABLE = False

logger = get_logger(__name__)


class RAGSystem:
    """Système RAG pour la recherche d'événements culturels."""

    def __init__(
        self,
        index_path: Optional[str] = None,
        model_name: Optional[str] = None,
        use_mistral_embeddings: Optional[bool] = None,
    ):
        """
        Initialise le système RAG.

        Args:
            index_path: Chemin vers l'index FAISS
            model_name: Nom du modèle Mistral pour le LLM
            use_mistral_embeddings: Si True, utilise Mistral pour embeddings, sinon HuggingFace
        """
        self.index_path = Path(index_path or settings.faiss_index_path)
        self.model_name = model_name or settings.mistral_model_name
        self.use_mistral_embeddings = use_mistral_embeddings if use_mistral_embeddings is not None else settings.use_mistral_embeddings

        self.embeddings = None
        self.vectorstore = None
        self.llm = None
        self.qa_chain = None
        self.retriever = None
        self.reranker = None

        logger.info("Système RAG initialisé")

    def load_index(self) -> None:
        """Charge l'index FAISS depuis le disque."""
        if not self.index_path.exists():
            raise FileNotFoundError(
                f"Index FAISS introuvable: {self.index_path}. "
                "Veuillez construire l'index avec /rebuild ou scripts/build_index.py"
            )

        logger.info(f"Chargement de l'index FAISS depuis {self.index_path}")

        # Charger les embeddings selon la configuration
        if self.use_mistral_embeddings:
            if not MISTRAL_AVAILABLE:
                logger.error("Mistral demandé mais langchain-mistralai n'est pas installé")
                raise ImportError("langchain-mistralai n'est pas installé")
            
            logger.info(f"Utilisation de Mistral AI Embeddings: {settings.mistral_embedding_model}")
            self.embeddings = MistralAIEmbeddings(
                model=settings.mistral_embedding_model,
                api_key=SecretStr(settings.mistral_api_key),
            )
        else:
            logger.info(f"Utilisation de HuggingFace Embeddings: {settings.huggingface_embedding_model}")
            self.embeddings = HuggingFaceEmbeddings(
                model_name=settings.huggingface_embedding_model,
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True},
            )

        # Charger le vectorstore
        self.vectorstore = FAISS.load_local(
            str(self.index_path),
            self.embeddings,
            allow_dangerous_deserialization=True,
        )

        logger.info(f"Index FAISS chargé: {self.vectorstore.index.ntotal} vecteurs")

    def initialize_llm(self) -> None:
        """Initialise le modèle de langage Mistral."""
        logger.info(f"Initialisation du modèle {self.model_name}")

        self.llm = ChatMistralAI(
            model=self.model_name,
            api_key=SecretStr(settings.mistral_api_key),
            temperature=settings.mistral_temperature,
            max_tokens=settings.mistral_max_tokens,
        )

        logger.info("LLM Mistral initialisé")

    def initialize_reranker(self) -> None:
        """Initialise le modèle de reranking si activé."""
        if not settings.rag_enable_reranking:
            logger.info("Reranking désactivé")
            return

        if not RERANKER_AVAILABLE:
            logger.warning("Reranking demandé mais sentence-transformers n'est pas installé")
            return

        logger.info("Initialisation du cross-encoder pour le reranking")
        # Modèle multilingue optimisé pour le français
        self.reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
        logger.info("Cross-encoder initialisé")

    def rerank_documents(self, query: str, documents: list) -> list:
        """Rerank les documents selon leur pertinence avec la requête."""
        if not self.reranker or not settings.rag_enable_reranking:
            return documents

        # Créer les paires (query, doc) pour le reranking
        pairs = [[query, doc.page_content] for doc in documents]
        
        # Calculer les scores
        scores = self.reranker.predict(pairs)
        
        # Trier les documents par score décroissant
        doc_score_pairs = list(zip(documents, scores))
        doc_score_pairs.sort(key=lambda x: x[1], reverse=True)
        
        reranked_docs = [doc for doc, score in doc_score_pairs]
        logger.info(f"Documents reranked: {len(reranked_docs)} documents")
        
        return reranked_docs

    def setup_qa_chain(self) -> None:
        """Configure la chaîne de Q&A avec prompt personnalisé."""
        if not self.vectorstore:
            raise ValueError("Le vectorstore doit être chargé avant de configurer la chaîne Q&A")

        if not self.llm:
            raise ValueError("Le LLM doit être initialisé avant de configurer la chaîne Q&A")

        self.retriever = self.vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": settings.rag_top_k,
                "fetch_k": settings.rag_top_k * 2
            }
        )

        prompt = ChatPromptTemplate.from_template(ANTI_HALLUCINATION_PROMPT)

        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        # Si reranking activé, on récupère plus de documents puis on rerank
        def retrieve_and_rerank(question: str):
            docs = self.retriever.invoke(question)
            if settings.rag_enable_reranking and self.reranker:
                docs = self.rerank_documents(question, docs)
            return format_docs(docs)

        self.qa_chain = (
            {
                "context": retrieve_and_rerank,
                "question": RunnablePassthrough()
            }
            | prompt
            | self.llm
            | StrOutputParser()
        )

        rerank_status = "avec reranking" if settings.rag_enable_reranking else "sans reranking"
        logger.info(f"Chaîne Q&A configurée avec MMR {rerank_status}")

    def query(
        self, question: str, return_sources: bool = False
    ) -> dict[str, Any]:
        """
        Pose une question au système RAG.

        Args:
            question: Question à poser
            return_sources: Si True, retourne les sources utilisées

        Returns:
            Dictionnaire avec la réponse et éventuellement les sources
        """
        if not self.qa_chain:
            raise ValueError("La chaîne Q&A n'est pas configurée")

        logger.info(f"Question reçue: {question}")

        # Exécuter la requête
        answer = self.qa_chain.invoke(question)

        response = {
            "question": question,
            "answer": answer,
        }

        # Ajouter les sources seulement si la réponse contient des informations (pas "non disponible" ou "n'ai pas trouvé")
        if return_sources and not any(phrase in answer.lower() for phrase in ["non disponible", "n'ai pas trouvé", "pas trouvé", "aucun événement"]):
            docs = self.retriever.invoke(question)
            # Appliquer le reranking si activé
            if settings.rag_enable_reranking and self.reranker:
                docs = self.rerank_documents(question, docs)
            sources = []
            for doc in docs[:settings.rag_rerank_top_n]:
                source = {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                }
                # Extraire les informations principales
                if "title" in doc.metadata:
                    source["title"] = doc.metadata["title"]
                if "location_city" in doc.metadata:
                    source["location"] = doc.metadata["location_city"]

                sources.append(source)

            response["sources"] = sources

        logger.info(f"Réponse générée avec {len(response.get('sources', []))} sources")

        return response


# Instance singleton
_rag_system: Optional[RAGSystem] = None


def get_rag_system() -> RAGSystem:
    """Récupère l'instance singleton du système RAG."""
    global _rag_system
    if _rag_system is None:
        _rag_system = RAGSystem()
    return _rag_system