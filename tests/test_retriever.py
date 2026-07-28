import pytest
from api.schemas import FilePayload
from storage.vector_store import vector_store
from workers.ingestor import ingest_files
from workers.retriever import bm25_search, hybrid_search, synthesise_answer

def test_hybrid_search_and_synthesis() -> None:
    """Verifies hybrid search retrieval and answer synthesis with citations.
    
    Parameters: none.
    Returns: None.
    """
    files = [
        FilePayload(path="arch.md", content="The core orchestrator receives query requests and dispatches work.", type="md")
    ]
    ingest_files(files, "tag1")
    
    chunks = hybrid_search("orchestrator query requests", project_tag="tag1")
    assert len(chunks) > 0
    
    answer, citations = synthesise_answer("orchestrator query requests", chunks)
    assert len(citations) > 0
    assert citations[0].source == "arch.md"
    assert "source: arch.md" in answer
