import re
from typing import Any, Dict, Generator, List, Optional, Tuple
from api.schemas import Citation
from storage.vector_store import vector_store
from workers.ingestor import mock_or_anthropic_embedding

def bm25_search(query: str, top_k: int = 8, project_tag: Optional[str] = None) -> List[Dict[str, Any]]:
    """Performs keyword BM25 search matching terms against stored chunks.
    
    Parameters:
        query: Natural language query string.
        top_k: Maximum top candidate records to return.
        project_tag: Optional tag filter.
    Returns:
        List of matching record dicts with BM25 score.
    """
    terms = set(re.findall(r'\w+', query.lower()))
    candidates = getattr(vector_store, "_data", [])
    if project_tag:
        candidates = [r for r in candidates if r.get("metadata", {}).get("project_tag") == project_tag]
        
    scored = []
    for r in candidates:
        words = set(re.findall(r'\w+', r["text"].lower()))
        match_count = len(terms.intersection(words))
        if match_count > 0:
            item = dict(r)
            item["score"] = float(match_count)
            scored.append(item)
            
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]

def hybrid_search(query: str, project_tag: Optional[str] = None) -> List[Dict[str, Any]]:
    """Combines vector similarity (top-8) and BM25 search (top-8) re-ranking to top-5.
    
    Parameters:
        query: Query string.
        project_tag: Optional project tag filter.
    Returns:
        List of top-5 deduplicated and re-ranked chunk records.
    """
    query_emb = mock_or_anthropic_embedding(query)
    vec_results = vector_store.search_similar(query_emb, top_k=8, project_tag=project_tag)
    bm25_results = bm25_search(query, top_k=8, project_tag=project_tag)
    
    dedup: Dict[str, Dict[str, Any]] = {}
    for r in vec_results:
        dedup[r["id"]] = dict(r)
    for r in bm25_results:
        if r["id"] in dedup:
            dedup[r["id"]]["score"] = dedup[r["id"]]["score"] + 0.5 * r["score"]
        else:
            dedup[r["id"]] = dict(r)
            
    sorted_chunks = sorted(dedup.values(), key=lambda x: x["score"], reverse=True)
    return sorted_chunks[:5]

def extract_citations(chunks: List[Dict[str, Any]]) -> List[Citation]:
    """Extracts structured citations from retrieved context chunks.
    
    Parameters:
        chunks: List of context chunk records.
    Returns:
        List of Citation objects.
    """
    citations = []
    for c in chunks:
        meta = c.get("metadata", {})
        citations.append(Citation(
            source=meta.get("source_path", "unknown"),
            chunk=meta.get("chunk_index", 0)
        ))
    return citations

def synthesise_answer(query: str, chunks: List[Dict[str, Any]]) -> Tuple[str, List[Citation]]:
    """Synthesises an answer with inline citations from top retrieved chunks.
    
    Parameters:
        query: User query string.
        chunks: Top retrieved context chunks.
    Returns:
        Tuple of (answer_text, citations_list).
    """
    citations = extract_citations(chunks)
    if not chunks:
        return "No relevant documentation found for your query.", []
        
    context_lines = []
    for c in chunks:
        src = c["metadata"].get("source_path", "file")
        idx = c["metadata"].get("chunk_index", 0)
        context_lines.append(f"[{c['text']}] [source: {src}, chunk {idx}]")
        
    answer = f"Based on the technical documentation:\n\n" + "\n\n".join(context_lines)
    return answer, citations

def synthesise_answer_stream(query: str, chunks: List[Dict[str, Any]]) -> Generator[str, None, None]:
    """Streams synthesised answer chunks for progressive SSE delivery.
    
    Parameters:
        query: User query string.
        chunks: Context chunks.
    Returns:
        Generator yielding text chunks.
    """
    full_answer, _ = synthesise_answer(query, chunks)
    words = full_answer.split(" ")
    for i in range(0, len(words), 4):
        yield " ".join(words[i:i+4]) + " "
