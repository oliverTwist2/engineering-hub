import pytest
from fastapi.testclient import TestClient
from config import settings
from main import app

client = TestClient(app)
AUTH_HEADERS = {"X-API-Key": settings.api_key}

def test_unauthorized_access() -> None:
    """Verifies 401 response when X-API-Key header is missing.
    
    Parameters: none.
    Returns: None.
    """
    res = client.get("/eval/summary")
    assert res.status_code == 401

def test_ingest_and_query_endpoints() -> None:
    """Verifies POST /ingest and POST /query integration flow.
    
    Parameters: none.
    Returns: None.
    """
    ingest_payload = {
        "files": [
            {"path": "incident_01.md", "content": "Database outage caused by connection pool exhaustion.", "type": "md"}
        ],
        "project_tag": "incident-reports"
    }
    ingest_res = client.post("/ingest", json=ingest_payload, headers=AUTH_HEADERS)
    assert ingest_res.status_code == 200
    assert ingest_res.json()["ingested"] == 1
    
    query_payload = {
        "question": "What caused the database outage?",
        "project_tag": "incident-reports",
        "stream": False
    }
    query_res = client.post("/query", json=query_payload, headers=AUTH_HEADERS)
    assert query_res.status_code == 200
    data = query_res.json()
    assert "answer" in data
    assert data["quality_score"] > 0.0

def test_eval_summary_endpoint() -> None:
    """Verifies GET /eval/summary endpoint telemetry report.
    
    Parameters: none.
    Returns: None.
    """
    res = client.get("/eval/summary", headers=AUTH_HEADERS)
    assert res.status_code == 200
    summary = res.json()
    assert "total_queries" in summary
    assert "avg_quality" in summary
