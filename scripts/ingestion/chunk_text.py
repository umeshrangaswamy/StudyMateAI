import logging
from typing import List

logger = logging.getLogger(__name__)

def chunk_text(text: str, chunk_size_tokens: int = 300, overlap_percent: float = 0.1) -> List[str]:
    """
    Splits text content into chunks of approximately chunk_size_tokens (using word-splitting 
    approximation) with overlap_percent sliding offset.
    """
    words = text.split()
    total_words = len(words)
    
    if total_words == 0:
        return []
        
    overlap_tokens = int(chunk_size_tokens * overlap_percent)
    step = chunk_size_tokens - overlap_tokens
    
    # Enforce safe minimum step to avoid infinite loops
    if step <= 0:
        step = 1

    chunks = []
    i = 0
    while i < total_words:
        chunk_words = words[i : i + chunk_size_tokens]
        chunks.append(" ".join(chunk_words))
        
        # Break if we have processed all words
        if i + chunk_size_tokens >= total_words:
            break
            
        i += step
        
    logger.info(
        f"Split input document of {total_words} words into {len(chunks)} chunks "
        f"(size={chunk_size_tokens} words, overlap={overlap_tokens} words)"
    )
    return chunks
