import hashlib
from typing import Dict, List, Optional

def compute_content_hash(content: str) -> str:
    """Computes a SHA256 hex digest for a given text or data string content.
    
    Parameters:
        content: Input text or string payload.
    Returns:
        SHA256 hex digest string.
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

class EmbeddingCache:
    """In-memory content-hash cache for chunk vector embeddings."""
    
    def __init__(self) -> None:
        """Initializes an empty embedding cache dictionary.
        
        Parameters: none.
        Returns: None.
        """
        self._cache: Dict[str, List[float]] = {}

    def get(self, content_hash: str) -> Optional[List[float]]:
        """Retrieves cached vector embedding for a content hash if present.
        
        Parameters:
            content_hash: SHA256 hash key of the content chunk.
        Returns:
            List of floats (vector embedding) or None if missing.
        """
        return self._cache.get(content_hash)

    def set(self, content_hash: str, embedding: List[float]) -> None:
        """Stores a computed vector embedding keyed by content hash.
        
        Parameters:
            content_hash: SHA256 hash key.
            embedding: Computed floating point vector embedding list.
        Returns: None.
        """
        self._cache[content_hash] = embedding

    def has(self, content_hash: str) -> bool:
        """Checks if an embedding exists in cache for the given content hash.
        
        Parameters:
            content_hash: SHA256 hash key to check.
        Returns:
            Boolean true if cache contains the hash, false otherwise.
        """
        return content_hash in self._cache

embedding_cache = EmbeddingCache()
