import os
import pytest
from storage.vector_store import ChromaVectorStore, cosine_similarity
from storage.metadata_db import init_db, log_evaluation, get_eval_summary

def test_cosine_similarity() -> None:
    """Verifies cosine similarity calculations for orthogonal and parallel vectors.
    
    Parameters: none.
    Returns: None.
    """
    v1 = [1.0, 0.0]
    v2 = [1.0, 0.0]
    v3 = [0.0, 1.0]
    assert cosine_similarity(v1, v2) == 1.0
    assert cosine_similarity(v1, v3) == 0.0

def test_vector_store_operations() -> None:
    """Verifies storing, searching, and deleting records in ChromaVectorStore.
    
    Parameters: none.
    Returns: None.
    """
    store = ChromaVectorStore()
    record = {
        "id": "c1",
        "text": "architecture diagram description",
        "embedding": [0.5, 0.5],
        "metadata": {"source_path": "doc.png", "project_tag": "projA"}
    }
    store.store_chunks([record])
    results = store.search_similar([0.5, 0.5], top_k=5, project_tag="projA")
    assert len(results) == 1
    assert results[0]["id"] == "c1"
    
    store.delete_by_project("projA")
    assert len(store.search_similar([0.5, 0.5], top_k=5)) == 0

def test_metadata_db_evaluation_logging() -> None:
    """Verifies logging query evaluation records and computing summary stats.
    
    Parameters: none.
    Returns: None.
    """
    init_db()
    row_id = log_evaluation(
        query="What is the architecture?",
        retrieved_chunks=[{"text": "arch details"}],
        quality_score=8.5,
        final_answer="The architecture uses FastAPI.",
        citations=[{"source": "arch.md", "chunk": 0}]
    )
    assert row_id > 0
    summary = get_eval_summary()
    assert summary["total_queries"] >= 1
    assert summary["avg_quality"] >= 0.0
    assert "arch.md" in summary["source_coverage"]
