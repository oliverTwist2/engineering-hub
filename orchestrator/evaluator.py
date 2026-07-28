import re
from typing import Any, Dict, List

def evaluate_quality(query: str, answer: str, chunks: List[Dict[str, Any]]) -> float:
    """Scores answer quality from 0.0 to 10.0 based on chunk relevance and completeness.
    
    Parameters:
        query: Original natural language question.
        answer: Generated answer response text.
        chunks: List of retrieved context chunk records.
    Returns:
        Float quality score bounded between 0.0 and 10.0.
    """
    if not chunks or "no relevant documentation" in answer.lower():
        return 2.0
        
    score = 4.0  # Base starting score for non-empty result
    
    # Citation presence boost (+3.0)
    has_citations = bool(re.search(r'\[source:\s*[^,]+,\s*chunk\s*\d+\]', answer))
    if has_citations:
        score += 3.0
        
    # Query keyword coverage in answer (+3.0)
    query_terms = set(re.findall(r'\w+', query.lower()))
    answer_words = set(re.findall(r'\w+', answer.lower()))
    if query_terms:
        match_ratio = len(query_terms.intersection(answer_words)) / len(query_terms)
        score += round(match_ratio * 3.0, 2)
        
    return min(10.0, max(0.0, round(score, 1)))
