"""
Configuration de l'application via variables d'environnement.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configuration de l'application."""

    # API Configuration
    api_version: str = "1.0.0"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True
    environment: str = "development"

    # OpenAgenda Configuration
    openagenda_api_key: str = ""
    openagenda_base_url: str = "https://api.openagenda.com/v2"
    openagenda_agenda_uid: str = ""
    openagenda_location: str = "Paris"
    openagenda_max_events: int = 500

    # Mistral AI Configuration
    mistral_api_key: str = ""
    mistral_model_name: str = "ministral-14b-2512"
    mistral_evaluator_model: str = "ministral-14b-2512"
    mistral_temperature: float = 0.3
    mistral_max_tokens: int = 1024

    # Embeddings Configuration
    use_mistral_embeddings: bool = True
    mistral_embedding_model: str = "mistral-embed-2312"
    huggingface_embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

    # FAISS Configuration
    faiss_index_path: str = "data/index/faiss_index"
    faiss_index_type: str = "Flat"
    faiss_nprobe: int = 10

    # RAG Configuration
    rag_top_k: int = 10  
    rag_chunk_size: int = 300
    rag_chunk_overlap: int = 50
    rag_enable_reranking: bool = True
    rag_rerank_top_n: int = 4  

    # Logging Configuration
    log_level: str = "INFO"
    log_file: Optional[str] = "logs/app.log"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    @property
    def embedding_model_name(self) -> str:
        """Retourne le nom du modèle d'embedding selon la configuration."""
        if self.use_mistral_embeddings:
            return self.mistral_embedding_model
        return self.huggingface_embedding_model

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()
