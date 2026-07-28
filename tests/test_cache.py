import pytest
from utils.cache import compute_content_hash, EmbeddingCache

def test_compute_content_hash() -> None:
    """Verifies consistent SHA256 hashing of string contents.
    
    Parameters: none.
    Returns: None.
    """
    h1 = compute_content_hash("sample content")
    h2 = compute_content_hash("sample content")
    h3 = compute_content_hash("different content")
    assert h1 == h2
    assert h1 != h3

def test_embedding_cache_operations() -> None:
    """Verifies set, get, and has operations on EmbeddingCache instance.
    
    Parameters: none.
    Returns: None.
    """
    cache = EmbeddingCache()
    c_hash = compute_content_hash("test chunk")
    embedding = [0.1, 0.2, 0.3]
    
    assert cache.has(c_hash) is False
    assert cache.get(c_hash) is None
    
    cache.set(c_hash, embedding)
    assert cache.has(c_hash) is True
    assert cache.get(c_hash) == embedding
