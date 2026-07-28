"""
Engineering Intelligence Hub — Interactive CLI
================================================
Starts the FastAPI server in the background and opens an interactive
terminal session so you can query the hub without curl or Postman.

Usage:
    python cli.py
"""

import json
import os
import sys
import textwrap
import threading
import time

import httpx
import uvicorn
from config import settings

# ── Config (reads from .env via pydantic-settings) ─────────────────────────
BASE_URL = "http://localhost:8000"
API_KEY  = settings.api_key

HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json",
}

# ── ANSI colour helpers ──────────────────────────────────────────────────────
class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    DIM    = "\033[2m"
    CYAN   = "\033[96m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    RED    = "\033[91m"
    BLUE   = "\033[94m"
    MAGENTA= "\033[95m"

def c(colour: str, text: str) -> str:
    return f"{colour}{text}{C.RESET}"

# ── Server bootstrap ─────────────────────────────────────────────────────────
def _run_server() -> None:
    """Runs the uvicorn server in a daemon thread."""
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_level="error",   # suppress server noise in the CLI session
        reload=False,
    )

def start_server() -> None:
    """Starts the FastAPI server in the background and waits until it is ready."""
    t = threading.Thread(target=_run_server, daemon=True)
    t.start()

    print(c(C.DIM, "  Starting server"), end="", flush=True)
    for _ in range(30):           # wait up to ~15 s
        time.sleep(0.5)
        print(c(C.DIM, "."), end="", flush=True)
        try:
            httpx.get(f"{BASE_URL}/docs", timeout=1)
            print()
            return
        except httpx.RequestError:
            continue

    print()
    print(c(C.RED, "  ✗ Server did not start in time. Check for port conflicts on :8000."))
    sys.exit(1)

# ── API helpers ──────────────────────────────────────────────────────────────
def do_query(question: str, project_tag: str | None = None) -> None:
    payload: dict = {"question": question, "stream": False}
    if project_tag:
        payload["project_tag"] = project_tag

    try:
        resp = httpx.post(f"{BASE_URL}/query", json=payload, headers=HEADERS, timeout=60)
        resp.raise_for_status()
    except httpx.HTTPStatusError as exc:
        print(c(C.RED, f"  ✗ HTTP {exc.response.status_code}: {exc.response.text}"))
        return
    except httpx.RequestError as exc:
        print(c(C.RED, f"  ✗ Request failed: {exc}"))
        return

    data = resp.json()

    print()
    print(c(C.GREEN, "  ┌─ Answer " + "─" * 60))
    wrapped = textwrap.fill(data.get("answer", ""), width=74,
                            initial_indent="  │  ", subsequent_indent="  │  ")
    print(wrapped)
    print(c(C.GREEN, "  └" + "─" * 69))

    citations = data.get("citations", [])
    if citations:
        print(c(C.CYAN, f"\n  Sources ({len(citations)}):"))
        for cit in citations:
            chunk_num = cit["chunk"]
            print(f"    {c(C.DIM, '·')} {cit['source']}  {c(C.DIM, f'chunk {chunk_num}')}")

    score = data.get("quality_score", 0)
    colour = C.GREEN if score >= 7 else (C.YELLOW if score >= 5 else C.RED)
    print(f"\n  Quality score: {c(colour, str(score))}/10\n")


def do_ingest_file(filepath: str, project_tag: str) -> None:
    """Reads a local file from disk and ingests it."""
    if not os.path.isfile(filepath):
        print(c(C.RED, f"  ✗ File not found: {filepath}"))
        return

    ext = os.path.splitext(filepath)[1].lstrip(".") or "txt"
    with open(filepath, "r", encoding="utf-8", errors="ignore") as fh:
        content = fh.read()

    payload = {
        "project_tag": project_tag,
        "files": [{"path": filepath, "content": content, "type": ext}],
    }

    try:
        resp = httpx.post(f"{BASE_URL}/ingest", json=payload, headers=HEADERS, timeout=60)
        resp.raise_for_status()
    except httpx.HTTPStatusError as exc:
        print(c(C.RED, f"  ✗ HTTP {exc.response.status_code}: {exc.response.text}"))
        return
    except httpx.RequestError as exc:
        print(c(C.RED, f"  ✗ Request failed: {exc}"))
        return

    data = resp.json()
    print(c(C.GREEN, f"  ✓ Ingested: {data['ingested']}  Skipped: {data['skipped']}"))
    for err in data.get("errors", []):
        print(c(C.RED, f"    ✗ {err['file']}: {err['reason']}"))
    print()


def do_stats() -> None:
    try:
        resp = httpx.get(f"{BASE_URL}/eval/summary", headers=HEADERS, timeout=10)
        resp.raise_for_status()
    except httpx.HTTPStatusError as exc:
        print(c(C.RED, f"  ✗ HTTP {exc.response.status_code}: {exc.response.text}"))
        return
    except httpx.RequestError as exc:
        print(c(C.RED, f"  ✗ Request failed: {exc}"))
        return

    data = resp.json()
    score = data.get("avg_quality", 0)
    colour = C.GREEN if score >= 7 else (C.YELLOW if score >= 5 else C.RED)

    print()
    print(c(C.CYAN, "  ┌─ Evaluation Summary " + "─" * 47))
    print(f"  │  Total queries   : {data.get('total_queries', 0)}")
    print(f"  │  Avg quality     : {c(colour, str(score))}/10")

    low_q = data.get("low_quality_queries", [])
    if low_q:
        print(f"  │  Low-quality     : {len(low_q)} query/queries flagged")

    coverage = data.get("source_coverage", {})
    if coverage:
        print(f"  │  Top cited sources:")
        for src, count in sorted(coverage.items(), key=lambda x: -x[1])[:5]:
            print(f"  │    {c(C.DIM, '·')} {src}  ({count} citations)")

    print(c(C.CYAN, "  └" + "─" * 69))
    print()


def print_banner() -> None:
    print()
    print(c(C.BOLD + C.MAGENTA, "  ╔══════════════════════════════════════════════════════════╗"))
    print(c(C.BOLD + C.MAGENTA, "  ║       Engineering Intelligence Hub  —  Interactive CLI   ║"))
    print(c(C.BOLD + C.MAGENTA, "  ╚══════════════════════════════════════════════════════════╝"))
    print()
    print(c(C.DIM, f"  Server : {BASE_URL}"))
    print(c(C.DIM, f"  API key: {API_KEY[:4]}{'*' * max(0, len(API_KEY) - 4)}"))
    print()


def print_help() -> None:
    print()
    print(c(C.YELLOW, "  Commands:"))
    rows = [
        ("query <question>",          "Ask a question"),
        ("query -p <tag> <question>", "Ask within a specific project tag"),
        ("ingest <file>",             "Ingest a local file (auto-detects type)"),
        ("ingest <file> -p <tag>",    "Ingest with a project tag"),
        ("stats",                     "Show evaluation metrics"),
        ("help",                      "Show this help message"),
        ("exit / quit",               "Shut down and exit"),
    ]
    for cmd, desc in rows:
        print(f"    {c(C.CYAN, cmd):<40}  {c(C.DIM, desc)}")
    print()


# ── REPL ─────────────────────────────────────────────────────────────────────
def parse_and_dispatch(line: str) -> bool:
    """
    Parses a raw input line and calls the appropriate handler.
    Returns False when the user wants to exit.
    """
    parts = line.strip().split()
    if not parts:
        return True

    cmd = parts[0].lower()

    # ── exit ──────────────────────────────────────────────────────────────
    if cmd in ("exit", "quit", "q"):
        print(c(C.DIM, "\n  Bye!\n"))
        return False

    # ── help ──────────────────────────────────────────────────────────────
    if cmd in ("help", "h", "?"):
        print_help()
        return True

    # ── stats ─────────────────────────────────────────────────────────────
    if cmd == "stats":
        do_stats()
        return True

    # ── query ─────────────────────────────────────────────────────────────
    if cmd == "query":
        rest = parts[1:]
        project_tag = None

        # optional: query -p TAG <question>
        if len(rest) >= 2 and rest[0] == "-p":
            project_tag = rest[1]
            rest = rest[2:]

        question = " ".join(rest).strip()
        if not question:
            print(c(C.YELLOW, "  Usage: query [-p PROJECT_TAG] Your question here"))
            return True

        print(c(C.DIM, f"\n  Querying: \"{question}\"") +
              (c(C.DIM, f"  [project: {project_tag}]") if project_tag else ""))
        do_query(question, project_tag)
        return True

    # ── ingest ────────────────────────────────────────────────────────────
    if cmd == "ingest":
        rest = parts[1:]
        project_tag = "default"

        # optional: ingest <file> -p TAG
        if len(rest) >= 3 and rest[-2] == "-p":
            project_tag = rest[-1]
            rest = rest[:-2]

        filepath = " ".join(rest).strip()
        if not filepath:
            print(c(C.YELLOW, "  Usage: ingest <filepath> [-p PROJECT_TAG]"))
            return True

        print(c(C.DIM, f"\n  Ingesting: {filepath}  [project: {project_tag}]"))
        do_ingest_file(filepath, project_tag)
        return True

    print(c(C.YELLOW, f"  Unknown command: '{cmd}'.  Type 'help' for available commands."))
    return True


def run_repl() -> None:
    print_help()
    while True:
        try:
            line = input(c(C.BOLD + C.CYAN, "  hub> "))
        except (EOFError, KeyboardInterrupt):
            print(c(C.DIM, "\n  Interrupted — type 'exit' to quit.\n"))
            continue

        if not parse_and_dispatch(line):
            break


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print_banner()
    print(c(C.DIM, "  Booting server in background thread…"))
    start_server()
    print(c(C.GREEN, "  ✓ Server is ready.\n"))
    run_repl()
