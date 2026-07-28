import pytest
from api.schemas import FilePayload, QueryRequest
from orchestrator.agent import process_rag_query
from orchestrator.evaluator import evaluate_quality
from orchestrator.planner import decompose_query
from workers.ingestor import ingest_files

def test_planner_decomposition() -> None:
    """Verifies query planner splitting complex multi-topic queries.
    
    Parameters: none.
    Returns: None.
    """
    q1 = "What is the architecture?"
    assert decompose_query(q1) == [q1]
    
    q2 = "What is the ingestion pipeline and how does the retriever worker operate?"
    parts = decompose_query(q2)
    assert len(parts) == 2

def test_evaluator_scoring() -> None:
    """Verifies score calculation for answers with and without citations.
    
    Parameters: none.
    Returns: None.
    """
    query = "Where is config stored?"
    ans_no_cit = "Config is stored in config.py"
    ans_cit = "Config is stored in config.py [source: config.py, chunk 0]"
    chunks = [{"text": "config.py setup"}]
    
    score_low = evaluate_quality(query, ans_no_cit, chunks)
    score_high = evaluate_quality(query, ans_cit, chunks)
    assert score_high > score_low

def test_orchestrator_agent_flow() -> None:
    """Verifies end-to-end execution of Orchestrator process_rag_query.
    
    Parameters: none.
    Returns: None.
    """
    ingest_files([
        FilePayload(path="overview.md", content="The engineering hub system architecture uses FastAPI.", type="md")
    ], "projX")
    
    req = QueryRequest(question="What framework does the hub architecture use?", project_tag="projX")
    resp = process_rag_query(req)
    assert resp.quality_score >= 6.0
    assert len(resp.citations) > 0
