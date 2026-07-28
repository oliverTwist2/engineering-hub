# 🧠 Engineering Intelligence Hub

> A smart question-answering system for your engineering team's documentation.

---

## What is this?

The **Engineering Intelligence Hub** is a tool that lets engineers ask questions in plain English and get accurate answers pulled directly from your team's documentation, code files, and architecture diagrams.

Think of it like a very knowledgeable team member who has read every doc, diagram, and incident report — and can instantly point you to the right section with a source link.

**Example questions you can ask it:**
- *"How does our authentication service handle token expiry?"*
- *"What caused the database outage last March?"*
- *"What are the steps to deploy the payments microservice?"*

It responds with a written answer **and** tells you exactly which file and section it got the information from.

---

## Who is this for?

| Role | How it helps |
|---|---|
| **New engineers** | Get up to speed quickly without reading every doc |
| **Senior engineers** | Find information across large, sprawling codebases fast |
| **On-call engineers** | Look up incident history and troubleshooting steps instantly |
| **Tech leads** | Reduce the time spent answering repetitive questions |

---

## How it works (simple overview)

There are two main actions:

```
1. INGEST  →  You upload your docs/code files into the system
2. QUERY   →  You ask a question, and it searches those files and writes an answer
```

Under the hood, it uses a technique called **RAG (Retrieval-Augmented Generation)** — a way of combining smart search with AI to give answers that are grounded in your actual documentation rather than made up.

---

## Prerequisites

Before you start, make sure you have:

- ✅ **Python 3.11 or newer** — [Download here](https://www.python.org/downloads/)
- ✅ **An Anthropic API key** — [Get one here](https://console.anthropic.com/) (used by the AI models)

To check your Python version, open a terminal and run:
```bash
python --version
```

---

## Getting Started

### Step 1 — Install dependencies

Open a terminal in the project folder and run:

```bash
python -m pip install fastapi pydantic pydantic-settings httpx uvicorn pytest chromadb
```

### Step 2 — Set up your API key

Create a file called `.env` in the project root (same folder as `main.py`) and add:

```
ANTHROPIC_API_KEY=your-api-key-goes-here
API_KEY=choose-a-secret-key-for-this-hub
```

> **What is `API_KEY`?** This is a password you choose yourself to protect the Hub's API. You'll need to include it in every request you make. Pick any string you like, e.g. `my-secret-hub-key-123`.

### Step 3 — Start the server

```bash
python main.py
```

You should see output like:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

The Hub is now running! You can open your browser and visit `http://localhost:8000/docs` to see the interactive API documentation (provided automatically by FastAPI).

---

## Using the Hub

All requests to the Hub must include a header:
```
X-API-Key: <the API_KEY you set in your .env file>
```

### 📥 Ingesting documents

Before you can query anything, you need to feed documents into the Hub. You send your files as JSON to the `/ingest` endpoint.

**Example request (using `curl`):**

```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -H "X-API-Key: my-secret-hub-key-123" \
  -d '{
    "project_tag": "backend-api",
    "files": [
      {
        "path": "docs/architecture.md",
        "content": "Our backend uses a microservices architecture...",
        "type": "md"
      },
      {
        "path": "docs/auth-service.md",
        "content": "The auth service issues JWT tokens with a 1-hour expiry...",
        "type": "md"
      }
    ]
  }'
```

**What the fields mean:**

| Field | Description |
|---|---|
| `project_tag` | A label to group files together (e.g. `"backend-api"`, `"mobile-app"`) |
| `files[].path` | The filename/path you want to appear in citations |
| `files[].content` | The actual text content of the file |
| `files[].type` | The file type: `md`, `py`, `txt`, `pdf`, or `png`/`jpg` for images |

**Example response:**

```json
{
  "ingested": 2,
  "skipped": 0,
  "errors": []
}
```

> 💡 **Tip:** If you run ingest again with a file that hasn't changed, the Hub will skip it automatically — no duplicate data.

---

### 🔍 Querying for answers

Once documents are ingested, you can ask questions.

**Example request:**

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -H "X-API-Key: my-secret-hub-key-123" \
  -d '{
    "question": "How does the auth service handle token expiry?",
    "project_tag": "backend-api",
    "stream": false
  }'
```

**What the fields mean:**

| Field | Description |
|---|---|
| `question` | Your question in plain English |
| `project_tag` | *(Optional)* Filter to only search within a specific project's files |
| `stream` | Set to `true` to receive the answer word-by-word as it's generated |

**Example response:**

```json
{
  "answer": "Based on the technical documentation:\n\nThe auth service issues JWT tokens with a 1-hour expiry...",
  "citations": [
    {
      "source": "docs/auth-service.md",
      "chunk": 0
    }
  ],
  "quality_score": 8.5
}
```

**Understanding the response:**

| Field | Description |
|---|---|
| `answer` | The AI-generated answer based on your docs |
| `citations` | The exact files and sections the answer came from |
| `quality_score` | A score from 0–10 rating how confident the system is in the answer |

> 💡 **Tip:** If `quality_score` is below 6, the Hub automatically rephrases your question and retries once to try to give a better answer.

---

### 📊 Checking evaluation metrics

You can see stats on how the Hub has been performing:

```bash
curl http://localhost:8000/eval/summary \
  -H "X-API-Key: my-secret-hub-key-123"
```

**Example response:**

```json
{
  "total_queries": 47,
  "avg_quality": 7.8,
  "low_quality_queries": ["what is the meaning of life"],
  "source_coverage": {
    "docs/architecture.md": 12,
    "docs/auth-service.md": 8
  }
}
```

This tells you how many queries were run, what the average answer quality was, and which files are being cited the most.

---

## Supported File Types

| Type | Description |
|---|---|
| `.md` | Markdown files (README, wikis, runbooks) |
| `.py` | Python source code |
| `.txt` | Plain text files |
| `.pdf` | PDF documents |
| `.png`, `.jpg` | Architecture diagrams (the Hub will generate a text description) |

---

## Running the Tests

The project comes with 21 automated tests. To run them:

```bash
python -m pytest tests/ -v
```

All 21 tests should pass. This is a great way to verify everything is set up correctly.

---

## Configuration Reference

You can customise the Hub by adding these variables to your `.env` file:

| Variable | Default | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | *(required)* | Your Anthropic API key |
| `API_KEY` | `your-hub-api-key` | The secret key to protect your Hub's API |
| `VECTOR_BACKEND` | `chroma` | Vector database backend (`chroma` or `pgvector`) |
| `CHUNK_SIZE` | `512` | Number of tokens per text chunk |
| `CHUNK_OVERLAP` | `64` | Overlap between consecutive chunks |
| `INGEST_BATCH_SIZE` | `10` | Files processed per batch |

---

## Project Structure

```
engineering-hub/
├── main.py               # Start the server from here
├── config.py             # All configuration settings
├── .env                  # Your secrets (create this yourself)
│
├── api/
│   ├── routes.py         # The /ingest, /query, /eval/summary endpoints
│   └── schemas.py        # Data shapes for requests and responses
│
├── orchestrator/
│   ├── agent.py          # Runs the full RAG pipeline
│   ├── planner.py        # Breaks complex questions into sub-questions
│   └── evaluator.py      # Scores answer quality (0–10)
│
├── workers/
│   ├── ingestor.py       # Reads, chunks, and stores your files
│   └── retriever.py      # Searches stored chunks and synthesises answers
│
├── storage/
│   ├── vector_store.py   # Stores and searches document embeddings
│   └── metadata_db.py    # Logs query evaluations to SQLite
│
├── utils/
│   ├── chunker.py        # Splits long text into overlapping chunks
│   ├── file_parser.py    # Extracts text from different file formats
│   └── cache.py          # Avoids re-embedding identical content
│
└── tests/                # 21 automated tests
```

---

## Glossary

**RAG (Retrieval-Augmented Generation):** A technique where an AI looks up relevant information from a database before writing its answer, so answers are grounded in real documents rather than general training data.

**Embedding:** A numerical representation of text that captures its meaning. Similar texts have similar embeddings, allowing the system to find related content even if the exact words don't match.

**Vector Store:** A database optimised for storing and searching embeddings.

**Chunk:** A small piece of a document. Long files are split into chunks so they can be searched and retrieved more precisely.

**BM25:** A classic keyword-based search algorithm. The Hub combines this with vector search (hybrid search) to get the best of both approaches.

**Citation:** A reference back to the exact file and chunk that an answer was drawn from, so you can verify the source.

---

## Troubleshooting

**❌ `401 Unauthorized` error**
Your `X-API-Key` header is missing or incorrect. Double-check it matches the `API_KEY` in your `.env` file.

**❌ `No relevant documentation found for your query`**
The Hub hasn't ingested any files yet, or your query doesn't match the ingested content. Try the `/ingest` endpoint first.

**❌ Server won't start**
Make sure you've installed all dependencies (`pip install ...`) and that you're running Python 3.11+.

**❌ Tests fail**
Run `python -m pip install pytest fastapi pydantic pydantic-settings httpx uvicorn chromadb` to make sure all test dependencies are installed.
