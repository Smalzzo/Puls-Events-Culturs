#!/usr/bin/env python
"""
Script to build FAISS index from OpenAgenda events.
Run this before starting the API.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.indexer import build_index_from_openagenda
from src.logger import get_logger

logger = get_logger(__name__)


def main():
    """Main entry point."""
    try:
        logger.info("=" * 50)
        logger.info("Building FAISS index from OpenAgenda")
        logger.info("=" * 50)
        
        build_index_from_openagenda()
        
        logger.info("=" * 50)
        logger.info("Index build completed successfully!")
        logger.info("=" * 50)
        logger.info("You can now start the API with:")
        logger.info("  uvicorn api.main:app --reload")
        logger.info("Or use: make run")
        
    except Exception as e:
        logger.error(f"Failed to build index: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
