import re
from typing import List

def decompose_query(query: str) -> List[str]:
    """Decomposes a complex query into at most two sub-questions.
    
    Parameters:
        query: User natural language query string.
    Returns:
        List of sub-question strings (length 1 or 2).
    """
    clean_query = query.strip()
    if not clean_query:
        return [query]
        
    parts = re.split(r'\band\b|\balso\b|\bas well as\b', clean_query, flags=re.IGNORECASE)
    if len(parts) >= 2 and len(parts[0].strip()) > 5 and len(parts[1].strip()) > 5:
        q1 = parts[0].strip()
        q2 = parts[1].strip()
        if not q1.endswith("?"):
            q1 += "?"
        if not q2.endswith("?"):
            q2 += "?"
        return [q1, q2]
        
    return [clean_query]
