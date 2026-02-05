"""
FastAPI application for RAG-based cultural events search.
"""

from contextlib import asynccontextmanager
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from src.config import settings
from src.logger import get_logger
from src.rag import get_rag_system
from src.indexer import build_index_from_openagenda, FAISSIndexBuilder
from src.chunking import EventChunker

logger = get_logger(__name__)


# ===========================
# Pydantic Models
# ===========================

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    environment: str
    index_loaded: bool


class AskRequest(BaseModel):
    """Request model pour /ask."""
    question: str = Field(
        ...,
        description="Question sur les événements culturels",
        min_length=3,
        max_length=500,
    )


class AskResponse(BaseModel):
    """Response model pour /ask."""
    question: str
    answer: str
    sources: list[dict[str, Any]]


class RebuildRequest(BaseModel):
    """Request model pour /rebuild."""
    events: list[dict[str, Any]] = Field(
        ...,
        description="Liste des événements à ajouter à l'index existant"
    )


class RebuildResponse(BaseModel):
    """Response model pour /rebuild."""
    status: str
    message: str
    events_processed: int
    chunks_created: int


class EvaluateRequest(BaseModel):
    """Request model pour /evaluate."""
    test_file_path: Optional[str] = Field(
        default="data/test/ragas_questions.json",
        description="Chemin vers le fichier de questions de test"
    )


class EvaluateResponse(BaseModel):
    """Response model pour /evaluate."""
    status: str
    metrics: dict[str, float]
    message: str


# ===========================
# Lifespan
# ===========================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for application startup and shutdown."""
    # Startup
    logger.info("Starting application...")
    try:
        rag_system = get_rag_system()
        rag_system.load_index()
        rag_system.initialize_llm()
        rag_system.initialize_reranker()
        rag_system.setup_qa_chain()
        logger.info("RAG system loaded and ready")
    except Exception as e:
        logger.error(f"Failed to initialize RAG system: {e}", exc_info=True)
        logger.warning("Application started but RAG system is not available")

    yield

    # Shutdown
    logger.info("Shutting down application...")


# ===========================
# FastAPI App
# ===========================

app = FastAPI(
    title="API RAG Événements Culturels Île-de-France",
    version=settings.api_version,
    description="API pour interroger et gérer les événements culturels via RAG",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===========================
# Exception Handler
# ===========================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


# ===========================
# Endpoints
# ===========================

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check de l'API.
    
    Vérifie que l'application fonctionne et que l'index FAISS est chargé.
    """
    try:
        rag_system = get_rag_system()
        index_loaded = rag_system.vectorstore is not None

        return HealthResponse(
            status="healthy" if index_loaded else "degraded",
            version=settings.api_version,
            environment=settings.environment,
            index_loaded=index_loaded,
        )
    except Exception as e:
        logger.error(f"Erreur health check: {e}", exc_info=True)
        return HealthResponse(
            status="unhealthy",
            version=settings.api_version,
            environment=settings.environment,
            index_loaded=False,
        )


@app.post("/ask", response_model=AskResponse, tags=["RAG"])
async def ask_question(request: AskRequest):
    """
    Pose une question sur les événements culturels.
    
    Utilise le pipeline RAG complet :
    - Récupération de documents pertinents (FAISS)
    - Génération de réponse (Mistral AI)
    
    Args:
        request: Question à poser
    
    Returns:
        Réponse générée avec sources
    """
    logger.info(f"Question reçue: {request.question}")

    try:
        rag_system = get_rag_system()
        result = rag_system.query(
            question=request.question,
            return_sources=True,
        )

        logger.info(f"Réponse générée pour: {request.question}")
        
        return AskResponse(
            question=result["question"],
            answer=result["answer"],
            sources=result.get("sources", []),
        )

    except FileNotFoundError as e:
        logger.error(f"Index FAISS introuvable: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Index FAISS introuvable. Veuillez reconstruire l'index avec /rebuild",
        )
    except Exception as e:
        logger.error(f"Erreur lors du traitement de la question: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du traitement de la question: {str(e)}",
        )


@app.post("/rebuild", response_model=RebuildResponse, tags=["Index"])
async def rebuild_index(request: RebuildRequest):
    """
    Ajoute de nouveaux événements à l'index FAISS existant.
    
    Cette opération :
    - Prend une liste d'événements au format JSON
    - Crée des chunks de texte pour chaque événement
    - Génère des embeddings
    - Ajoute les documents à l'index FAISS existant
    
    IMPORTANT: Cette opération AJOUTE à l'index existant, elle ne le remplace pas.
    Pour recréer complètement l'index, utilisez scripts/build_index.py
    
    Args:
        request: Liste d'événements à ajouter
    
    Returns:
        Statut de l'ajout avec statistiques
    
    Example:
        ```json
        {
          "events": [
            {
              "title_fr": "Concert de Jazz",
              "description_fr": "Grande soirée jazz",
              "location_name": "Salle Pleyel",
              "location_city": "Paris",
              "firstdate_begin": "2025-01-25T19:00:00"
            }
          ]
        }
        ```
    """
    logger.info(f"Démarrage de la reconstruction de l'index avec {len(request.events)} événements...")

    try:
        # Validation des événements
        if not request.events:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La liste d'événements est vide"
            )

        # Traitement des événements - utiliser les mêmes paramètres que l'index principal
        chunker = EventChunker(
            chunk_size=settings.rag_chunk_size,
            overlap=settings.rag_chunk_overlap
        )
        documents = chunker.create_chunks(request.events)

        if not documents:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Aucun chunk de texte généré à partir des événements"
            )

        logger.info(f"{len(documents)} chunks générés depuis {len(request.events)} événements")

        # Charger l'index existant et ajouter les nouveaux documents
        from pathlib import Path
        if not Path(settings.faiss_index_path).exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Index FAISS inexistant. Veuillez d'abord construire l'index avec scripts/build_index.py"
            )

        logger.info("Chargement de l'index existant pour ajout de documents...")
        
        # Récupérer le système RAG actuel pour utiliser les mêmes embeddings
        rag_system = get_rag_system()
        if not rag_system.embeddings:
            rag_system.load_index()
        
        # Charger l'index existant
        from langchain_community.vectorstores import FAISS
        vectorstore = FAISS.load_local(
            str(settings.faiss_index_path),
            rag_system.embeddings,
            allow_dangerous_deserialization=True,
        )
        
        # Ajouter les nouveaux documents
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        vectorstore.add_texts(texts=texts, metadatas=metadatas)
        logger.info(f"{len(documents)} documents ajoutés à l'index existant")

        # Sauvegarder l'index mis à jour
        builder = FAISSIndexBuilder()
        builder.save_index(vectorstore, settings.faiss_index_path)
        
        # Recharger le RAG system avec l'index mis à jour
        rag_system.load_index()
        rag_system.setup_qa_chain()
        
        logger.info("Index FAISS mis à jour avec succès")
        
        return RebuildResponse(
            status="success",
            message="Événements ajoutés à l'index FAISS avec succès",
            events_processed=len(request.events),
            chunks_created=len(documents),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la reconstruction de l'index: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la reconstruction de l'index: {str(e)}",
        )


@app.post("/evaluate", response_model=EvaluateResponse, tags=["Evaluation"])
async def evaluate_rag(request: EvaluateRequest):
    """Évalue la qualité du système RAG avec RAGAS."""
    logger.info("Démarrage de l'évaluation RAGAS...")

    try:
        from src.ragas_eval import get_ragas_evaluator
        import numpy as np
        
        evaluator = get_ragas_evaluator()
        results = evaluator.evaluate_from_file(request.test_file_path)
        
        logger.info(f"Évaluation RAGAS terminée: {results}")
        
        # Les résultats RAGAS sont des listes, calculer la moyenne
        def safe_mean(value):
            """Calcule la moyenne si c'est une liste, sinon retourne la valeur."""
            if isinstance(value, (list, np.ndarray)):
                return float(np.mean(value))
            return float(value)
        
        metrics = {
            "faithfulness": safe_mean(results["faithfulness"]),
            "answer_relevancy": safe_mean(results["answer_relevancy"]),
            "context_precision": safe_mean(results["context_precision"]),
            "context_recall": safe_mean(results["context_recall"]),
        }
        
        logger.info(f"Métriques moyennes calculées: {metrics}")
        
        return EvaluateResponse(
            status="success",
            metrics=metrics,
            message=f"Évaluation RAGAS terminée avec {len(metrics)} métriques",
        )

    except FileNotFoundError as e:
        logger.error(f"Fichier de test introuvable: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fichier de test introuvable: {request.test_file_path}",
        )
    except KeyError as e:
        logger.error(f"Métrique manquante dans les résultats RAGAS: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Métrique manquante dans les résultats RAGAS: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Erreur lors de l'évaluation RAGAS: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'évaluation RAGAS: {str(e)}",
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        log_level=settings.log_level.lower(),
    )
