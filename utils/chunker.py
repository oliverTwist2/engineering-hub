from typing import List
from config import settings

def estimate_tokens(text: str) -> int:
    """Estimates the token count of a given string using word-level heuristics.
    
    Parameters:
        text: Input string to measure.
    Returns:
        Estimated integer number of tokens.
    """
    return len(text.split())

def chunk_text(text: str, chunk_size: int = settings.chunk_size, chunk_overlap: int = settings.chunk_overlap) -> List[str]:
    """Splits a document text into overlapping token chunks based on config bounds.
    
    Parameters:
        text: Raw document text string.
        chunk_size: Maximum token capacity per chunk.
        chunk_overlap: Number of overlapping tokens between consecutive chunks.
    Returns:
        List of text chunk strings.
    """
    words = text.split()
    if not words:
        return []
    
    step = max(1, chunk_size - chunk_overlap)
    chunks = []
    
    for i in range(0, len(words), step):
        chunk_words = words[i:i + chunk_size]
        chunk_str = " ".join(chunk_words)
        chunks.append(chunk_str)
        if i + chunk_size >= len(words):
            break
            
    return chunks
