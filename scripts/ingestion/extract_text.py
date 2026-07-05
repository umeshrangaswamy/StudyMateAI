import os
import logging

logger = logging.getLogger(__name__)

def extract_document_text(filepath: str) -> str:
    """
    Extracts raw text from text documents.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Source file not found at {filepath}")
        
    logger.info(f"Extracting content from '{os.path.basename(filepath)}'...")
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()
