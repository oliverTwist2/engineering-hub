import json
import sqlite3
import time
from typing import Any, Dict, List
from config import settings

def get_db_connection() -> sqlite3.Connection:
    """Creates a connection to the SQLite metadata and evaluation database and ensures schema exists.
    
    Parameters: none.
    Returns:
        Active sqlite3.Connection instance.
    """
    db_path = settings.database_url.replace("sqlite:///", "")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS eval_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT NOT NULL,
            retrieved_chunks_json TEXT NOT NULL,
            quality_score REAL NOT NULL,
            final_answer TEXT NOT NULL,
            citations_json TEXT NOT NULL,
            created_at REAL NOT NULL
        )
    """)
    conn.commit()
    return conn

def init_db() -> None:
    """Initializes the database schema for evaluation logs.
    
    Parameters: none.
    Returns: None.
    """
    conn = get_db_connection()
    conn.close()

def log_evaluation(query: str, retrieved_chunks: List[Dict[str, Any]], quality_score: float, final_answer: str, citations: List[Dict[str, Any]]) -> int:
    """Inserts a query evaluation record into the eval_logs table.
    
    Parameters:
        query: User natural language query string.
        retrieved_chunks: List of retrieved chunk dictionaries.
        quality_score: Evaluated quality score (0.0 to 10.0).
        final_answer: Synthesised answer text.
        citations: Citation metadata dictionary list.
    Returns:
        Inserted row ID integer.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    now = time.time()
    cursor.execute("""
        INSERT INTO eval_logs (query, retrieved_chunks_json, quality_score, final_answer, citations_json, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        query,
        json.dumps(retrieved_chunks),
        quality_score,
        final_answer,
        json.dumps(citations),
        now
    ))
    row_id = cursor.lastrowid or 0
    conn.commit()
    conn.close()
    return row_id

def get_eval_summary() -> Dict[str, Any]:
    """Calculates evaluation statistics across all logged system queries.
    
    Parameters: none.
    Returns:
        Dictionary containing total_queries, avg_quality, low_quality_queries, source_coverage.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT query, quality_score, citations_json FROM eval_logs")
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return {"total_queries": 0, "avg_quality": 0.0, "low_quality_queries": [], "source_coverage": {}}
        
    total = len(rows)
    avg_score = sum(r["quality_score"] for r in rows) / total
    low_queries = [r["query"] for r in rows if r["quality_score"] < 6.0]
    
    coverage: Dict[str, int] = {}
    for r in rows:
        citations = json.loads(r["citations_json"])
        for c in citations:
            src = c.get("source", "unknown")
            coverage[src] = coverage.get(src, 0) + 1
            
    return {
        "total_queries": total,
        "avg_quality": round(avg_score, 2),
        "low_quality_queries": low_queries,
        "source_coverage": coverage
    }
