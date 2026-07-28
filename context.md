# Engineering Intelligence Hub - Session Context

This document provides the complete context of the "Engineering Intelligence Hub" project creation. It is intended to be read by another AI IDE or agent to quickly understand the project's goals, architecture, technical decisions, and current state.

## 1. Project Background & Goal
The objective was to build a developer-focused Retrieval-Augmented Generation (RAG) system called the "Engineering Intelligence Hub".
It ingests technical documentation, architecture diagrams, code files, and incident reports. Engineers query it in natural language, and it returns accurate, cited answers with links back to the source material to reduce onboarding time and troubleshooting overhead.

The core design philosophy is: **Simple, readable code over clever code. No over-engineering.**

## 2. Technical Stack
*   **Language:** Python 3.11+
*   **Framework:** FastAPI for the API layer.
*   **Data Validation:** Pydantic v2 (including `pydantic-settings`).
*   **Vector Store:** Abstracted layer supporting ChromaDB (default local) and pgvector.
*   **Metadata & Evaluation Logging:** SQLite (`sqlite3`).
*   **Testing:** `pytest` and `fastapi.testclient`.

## 3. Architecture & File Structure
The project was built in `C:\Users\n\.gemini\antigravity\scratch\engineering-hub`.

```text
engineering-hub/
├── config.py             # Centralized settings (Pydantic BaseSettings)
├── main.py               # FastAPI entry point & DB lifespan init
├── api/
│   ├── routes.py         # /ingest, /query, /eval/summary endpoints
│   └── schemas.py        # Request/Response data models
├── orchestrator/
│   ├── agent.py          # RAG pipeline, retry logic, evaluation logging
│   ├── planner.py        # Splits complex queries into max 2 sub-questions
│   └── evaluator.py      # Quality scoring (0-10) based on relevance & citations
├── workers/
│   ├── ingestor.py       # Batch processing, chunking, embedding, caching, vision fallback
│   └── retriever.py      # Hybrid BM25 + Vector search, citation synthesis
├── storage/
│   ├── vector_store.py   # Vector storage abstraction
│   └── metadata_db.py    # SQLite manager for the eval_logs table
├── utils/
│   ├── chunker.py        # Token-based text chunking (default 512 size, 64 overlap)
│   ├── file_parser.py    # File format detection and extraction (code, md, pdf, images)
│   └── cache.py          # SHA256 content-hash embedding cache
└── tests/                # Comprehensive unit and integration test suite (21 tests)
```

## 4. Key Implementation Details & Decisions
*   **Offline/Mock Testing:** To allow the test suite to run without requiring a live Anthropic API key, a deterministic pseudo-embedding generator fallback was implemented in `workers/ingestor.py` (`mock_or_anthropic_embedding`).
*   **Hybrid Search:** The retriever uses a combination of Vector Cosine Similarity (top-8) and Keyword BM25 (top-8). Results are deduplicated and re-ranked to the top 5 chunks. Score formula: `CosineSimilarity + 0.5 * BM25Score`.
*   **Self-Correction:** If the Orchestrator's evaluator scores a synthesized answer below 6.0, it automatically rephrases the query (appending context like "technical details architecture implementation") and retries once.
*   **Database Fixes applied during session:** Addressed an issue where `pytest` would fail due to the `eval_logs` SQLite table missing. The `get_db_connection()` function in `storage/metadata_db.py` was updated to automatically execute `CREATE TABLE IF NOT EXISTS eval_logs` upon connection.
*   **Pydantic v2 Compliance:** Updated `config.py` to use `model_config = SettingsConfigDict(env_file=".env")` instead of the deprecated `class Config`.

## 5. Current State
*   **Codebase:** Fully implemented. All files adhere strictly to the rule of < 40 lines per function, with comprehensive docstrings and type hints.
*   **Testing:** The test suite (`pytest tests/ -v`) runs successfully with **21/21 tests passing**.
*   **Documentation:** Three primary markdown artifacts have been generated in the project history:
    1.  `implementation_plan.md`: The initial step-by-step roadmap.
    2.  `user_guide.md`: Non-technical documentation on what the hub is and how to use it.
    3.  `developer_guide.md`: Technical documentation detailing algorithms, DB schemas, and how to run/test the code.

## 6. How to Run
```bash
# Install dependencies
python -m pip install pytest fastapi pydantic pydantic-settings httpx uvicorn

# Run tests
python -m pytest tests/ -v

# Run the server
python main.py
```
