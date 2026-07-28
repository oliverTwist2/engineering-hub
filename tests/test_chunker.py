import pytest
from utils.chunker import chunk_text, estimate_tokens

def test_estimate_tokens() -> None:
    """Verifies that token estimation correctly counts word tokens.
    
    Parameters: none.
    Returns: None.
    """
    text = "Hello world engineering RAG system"
    assert estimate_tokens(text) == 5

def test_chunk_text_basic() -> None:
    """Verifies text chunking with small chunk size and overlap parameters.
    
    Parameters: none.
    Returns: None.
    """
    text = "one two three four five six seven eight nine ten"
    chunks = chunk_text(text, chunk_size=5, chunk_overlap=2)
    assert len(chunks) > 1
    assert "one two three four five" in chunks[0]
    assert "four five six seven eight" in chunks[1]

def test_chunk_text_empty() -> None:
    """Verifies chunking empty string returns an empty list.
    
    Parameters: none.
    Returns: None.
    """
    assert chunk_text("") == []
