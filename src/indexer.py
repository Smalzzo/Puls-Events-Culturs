"""
Récupérateur de données OpenAgenda et constructeur d'index FAISS.
Récupère les événements depuis l'API OpenDataSoft OpenAgenda et crée des embeddings vectoriels.
"""

import json
from pathlib import Path
from typing import Any, List, Optional

import requests
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from pydantic import SecretStr

# Import optionnel de Mistral
try:
    from langchain_mistralai import MistralAIEmbeddings
    MISTRAL_AVAILABLE = True
except ImportError:
    MISTRAL_AVAILABLE = False

from src.config import settings
from src.logger import get_logger
from src.chunking import EventChunker

logger = get_logger(__name__)


class OpenAgendaFetcher:
    """Récupère les événements depuis l'API OpenDataSoft OpenAgenda."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://public.opendatasoft.com/api/records/1.0",
        dataset_id: str = "evenements-publics-openagenda",
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.dataset_id = dataset_id
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({"Authorization": f"Apikey {api_key}"})

    def fetch_events(
        self,
        location_region: str | None = "Île-de-France",
        year: int = 2025,
    ) -> list[dict[str, Any]]:
        logger.info(
            f"Récupération des événements depuis OpenDataSoft OpenAgenda "
            f"(région: {location_region}, année: {year})"
        )

        url = f"{self.base_url}/search/"
        
        params = {
            "dataset": self.dataset_id,
            "rows": 100,
            "sort": "firstdate_begin",
        }

        if location_region:
            params["refine.location_region"] = location_region
        
        if year:
            params["q"] = f"firstdate_begin>={year}"

        all_events = []
        start = 0

        while True:
            params["start"] = start
            
            try:
                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()

                records = data.get("records", [])
                if not records:
                    break

                for record in records:
                    fields = record.get("fields", {})
                    all_events.append(fields)

                logger.info(f"Récupération de {len(all_events)} événements en cours...")

                total = data.get("nhits", 0)
                if len(all_events) >= total:
                    break

                start += len(records)

            except requests.RequestException as e:
                logger.error(f"Erreur lors de la récupération des événements: {e}")
                break

        logger.info(f"Total d'événements récupérés: {len(all_events)}")
        return all_events

    def save_raw_events(self, events: list[dict[str, Any]], output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(events, f, ensure_ascii=False, indent=2)
        logger.info(f"Sauvegarde de {len(events)} événements dans {output_path}")


class FAISSIndexBuilder:
    """Constructeur d'index FAISS."""

    def __init__(self, use_mistral: Optional[bool] = None):
        self.use_mistral = use_mistral if use_mistral is not None else settings.use_mistral_embeddings
        
        if self.use_mistral and not MISTRAL_AVAILABLE:
            logger.error("Mistral demandé mais langchain-mistralai n'est pas installé")
            logger.error("Installation requise: pip install langchain-mistralai")
            raise ImportError("langchain-mistralai n'est pas installé")
        
        if self.use_mistral:
            logger.info(f"Utilisation de Mistral AI Embeddings: {settings.mistral_embedding_model}")
            logger.info("Mode payant: 0.01 EUR/1M tokens")
            
            if not settings.mistral_api_key:
                raise ValueError("MISTRAL_API_KEY manquante dans les variables d'environnement")
            
            self.embeddings = MistralAIEmbeddings(
                model=settings.mistral_embedding_model,
                api_key=SecretStr(settings.mistral_api_key),
            )
            self.embedding_model_name = settings.mistral_embedding_model
        else:
            logger.info(f"Utilisation de HuggingFace: {settings.huggingface_embedding_model}")
            logger.info("Mode gratuit")
            
            self.embeddings = HuggingFaceEmbeddings(
                model_name=settings.huggingface_embedding_model,
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True},
            )
            self.embedding_model_name = settings.huggingface_embedding_model

        self.chunker = EventChunker(chunk_size=300, overlap=50)

    def create_documents(self, events: List[dict]) -> List[Document]:
        return self.chunker.create_chunks(events)

    def build_index(self, documents: List[Document]) -> FAISS:
        logger.info(f"Construction de l'index FAISS avec {len(documents)} documents")
        
        if self.use_mistral:
            total_chars = sum(len(doc.page_content) for doc in documents)
            estimated_tokens = total_chars // 4
            estimated_cost = (estimated_tokens / 1_000_000) * 0.01
            logger.warning(f"Coût estimé Mistral: environ {estimated_cost:.4f} EUR ({estimated_tokens:,} tokens)")

        vectorstore = FAISS.from_documents(documents, self.embeddings)

        logger.info(f"Index FAISS créé: {vectorstore.index.ntotal} vecteurs")
        return vectorstore

    def save_index(self, vectorstore: FAISS, path: Optional[str] = None) -> None:
        save_path = Path(path or settings.faiss_index_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Sauvegarde de l'index dans {save_path}")
        vectorstore.save_local(str(save_path))
        logger.info("Index sauvegardé avec succès")


def build_index_from_openagenda() -> None:
    logger.info("Démarrage du processus de construction de l'index...")
    
    logger.info(f"Config use_mistral_embeddings: {settings.use_mistral_embeddings}")
    logger.info(f"Config mistral_embedding_model: {settings.mistral_embedding_model}")
    logger.info(f"Config huggingface_embedding_model: {settings.huggingface_embedding_model}")
    
    if settings.use_mistral_embeddings:
        logger.warning("Mode PAYANT activé: Mistral Embed (0.01 EUR/1M tokens)")
    else:
        logger.info("Mode GRATUIT activé: HuggingFace")

    json_path = Path("data/raw/openagenda.json")
    
    if json_path.exists():
        logger.info(f"Fichier JSON existant trouvé: {json_path}")
        logger.info("Chargement des événements depuis le fichier...")
        
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                events = json.load(f)
            logger.info(f"{len(events)} événements chargés depuis le fichier")
        except Exception as e:
            logger.error(f"Erreur lors du chargement du fichier JSON: {e}")
            logger.info("Récupération depuis OpenAgenda...")
            events = None
    else:
        logger.info("Aucun fichier JSON trouvé, récupération depuis OpenAgenda...")
        events = None
    
    if events is None:
        fetcher = OpenAgendaFetcher()
        logger.info("Récupération des événements depuis OpenAgenda...")
        events = fetcher.fetch_events(
            location_region="Île-de-France",
            year=2025,
        )

        if not events:
            logger.error("Aucun événement récupéré")
            return

        fetcher.save_raw_events(events, json_path)

    builder = FAISSIndexBuilder()
    documents = builder.create_documents(events)
    vectorstore = builder.build_index(documents)
    builder.save_index(vectorstore, settings.faiss_index_path)

    logger.info("Construction de l'index terminée")


def main():
    build_index_from_openagenda()


if __name__ == "__main__":
    main()