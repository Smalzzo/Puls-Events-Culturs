"""
Module de logging pour l'application.
"""

import logging
import sys
from pathlib import Path

from src.config import settings


def setup_logging() -> None:
    """
    Configure le système de logging.
    
    Crée un logger avec:
    - Handler console (stdout)
    - Handler fichier (si spécifié)
    - Format personnalisé
    """
    # Configuration du format
    log_format = settings.log_format
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Formatter
    formatter = logging.Formatter(log_format, datefmt=date_format)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.log_level)
    
    # Supprimer les handlers existants
    root_logger.handlers.clear()
    
    # Handler console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(settings.log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Handler fichier (si configuré)
    if settings.log_file:
        log_file = Path(settings.log_file)
        
        # Créer le dossier logs si nécessaire
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(settings.log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Réduire le niveau de log pour les bibliothèques tierces
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
    logging.getLogger("transformers").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Récupère un logger avec le nom spécifié.
    
    Args:
        name: Nom du logger (généralement __name__)
    
    Returns:
        Logger configuré
    """
    return logging.getLogger(name)


class LoggerMixin:
    """
    Mixin pour ajouter un logger aux classes.
    
    Usage:
        class MyClass(LoggerMixin):
            def my_method(self):
                self.logger.info("Message")
    """
    
    @property
    def logger(self) -> logging.Logger:
        """Retourne un logger pour la classe."""
        name = f"{self.__class__.__module__}.{self.__class__.__name__}"
        return get_logger(name)


# Configuration automatique au chargement du module
setup_logging()
