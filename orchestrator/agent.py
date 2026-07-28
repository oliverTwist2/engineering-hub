from typing import Any, Dict, List, Optional, Tuple
from api.schemas import Citation, QueryRequest, QueryResponse
from orchestrator.evaluator import evaluate_quality
from orchestrator.planner import decompose_query
from storage.metadata_db import log_evaluation
from workers.retriever import hybrid_search, synthesise_answer, synthesise_answer_stream

def rephrase_query(original_query: str) -> str:
    """Rephrases a query for a single retry attempt when quality score is low.
    
    Parameters:
        original_query: Input query string that scored poorly.
    Returns:
        Rephrased expanded query string.
    """
    return f"{original_query} technical details architecture implementation"

def execute_single_query(query: str, project_tag: Optional[str]) -> Tuple[str, List[Dict[str, Any]], List[Citation]]:
    """Runs query decomposition, hybrid retrieval, and answer synthesis.
    
    Parameters:
        query: Target sub-query string.
        project_tag: Optional project classification tag.
    Returns:
        Tuple of (answer_string, retrieved_chunks_list, citations_list).
    """
    sub_questions = decompose_query(query)
    combined_answers = []
    all_chunks = []
    all_citations = []
    
    for sub_q in sub_questions:
        chunks = hybrid_search(sub_q, project_tag=project_tag)
        ans, cits = synthesise_answer(sub_q, chunks)
        combined_answers.append(ans)
        all_chunks.extend(chunks)
        all_citations.extend(cits)
        
    merged_answer = "\n\n".join(combined_answers)
    return merged_answer, all_chunks, all_citations

def process_rag_query(req: QueryRequest) -> QueryResponse:
    """Orchestrates end-to-end RAG query workflow including scoring, retry, and log evaluation.
    
    Parameters:
        req: QueryRequest object containing query parameters.
    Returns:
        QueryResponse object with final answer, citations, quality score.
    """
    answer, chunks, citations = execute_single_query(req.question, req.project_tag)
    score = evaluate_quality(req.question, answer, chunks)
    
    # Retry once if quality score below threshold 6.0
    if score < 6.0:
        rephrased = rephrase_query(req.question)
        alt_ans, alt_chunks, alt_cits = execute_single_query(rephrased, req.project_tag)
        alt_score = evaluate_quality(rephrased, alt_ans, alt_chunks)
        if alt_score > score:
            answer, chunks, citations, score = alt_ans, alt_chunks, alt_cits, alt_score
            
    cit_dicts = [{"source": c.source, "chunk": c.chunk} for c in citations]
    log_evaluation(req.question, chunks, score, answer, cit_dicts)
    return QueryResponse(answer=answer, citations=citations, quality_score=score)
