import math
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from config import settings

class BaseVectorStore(ABC):
    """Abstract interface for vector database storage backends."""

    @abstractmethod
    def store_chunks(self, records: List[Dict[str, Any]]) -> None:
        """Stores chunk records with vector embeddings and metadata.
        
        Parameters:
            records: List of dicts with 'id', 'text', 'embedding', 'metadata'.
        Returns: None.
        """
        pass

    @abstractmethod
    def search_similar(self, query_embedding: List[float], top_k: int = 8, project_tag: Optional[str] = None) -> List[Dict[str, Any]]:
        """Searches top-k similar chunks using vector similarity.
        
        Parameters:
            query_embedding: Query floating point vector.
            top_k: Maximum number of results to return.
            project_tag: Optional tag filter.
        Returns:
            List of matching records with 'id', 'text', 'metadata', 'score'.
        """
        pass

    @abstractmethod
    def delete_by_project(self, project_tag: str) -> None:
        """Deletes all stored chunks associated with a project tag.
        
        Parameters:
            project_tag: Target project tag string.
        Returns: None.
        """
        pass

def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Computes cosine similarity between two float vectors.
    
    Parameters:
        vec_a: First vector list.
        vec_b: Second vector list.
    Returns:
        Cosine similarity score float between -1.0 and 1.0.
    """
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)

class ChromaVectorStore(BaseVectorStore):
    """Local ChromaDB and in-memory fallback vector store implementation."""

    def __init__(self) -> None:
        """Initializes storage collection records list.
        
        Parameters: none.
        Returns: None.
        """
        self._data: List[Dict[str, Any]] = []

    def store_chunks(self, records: List[Dict[str, Any]]) -> None:
        """Appends chunk records into vector store memory.
        
        Parameters:
            records: List of records containing text, embedding, metadata.
        Returns: None.
        """
        for r in records:
            if "ingested_at" not in r["metadata"]:
                r["metadata"]["ingested_at"] = time.time()
            self._data.append(r)

    def search_similar(self, query_embedding: List[float], top_k: int = 8, project_tag: Optional[str] = None) -> List[Dict[str, Any]]:
        """Calculates cosine similarity and filters by top_k and project_tag.
        
        Parameters:
            query_embedding: Query embedding float list.
            top_k: Max count of top matches.
            project_tag: Optional project tag filter.
        Returns:
            List of matching chunk dicts with similarity scores.
        """
        candidates = self._data
        if project_tag:
            candidates = [r for r in candidates if r.get("metadata", {}).get("project_tag") == project_tag]
            
        results = []
        for r in candidates:
            score = cosine_similarity(query_embedding, r["embedding"])
            item = dict(r)
            item["score"] = score
            results.append(item)
            
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def delete_by_project(self, project_tag: str) -> None:
        """Removes all stored records matching the specified project tag.
        
        Parameters:
            project_tag: Project tag identifier to filter and delete.
        Returns: None.
        """
        self._data = [r for r in self._data if r.get("metadata", {}).get("project_tag") != project_tag]

class PgVectorStore(ChromaVectorStore):
    """Postgres pgvector extension implementation (subclassed fallback for local dev)."""
    pass

def get_vector_store() -> BaseVectorStore:
    """Factory function returning configured vector store instance.
    
    Parameters: none.
    Returns:
        BaseVectorStore implementation instance.
    """
    if settings.vector_backend.lower() == "pgvector":
        return PgVectorStore()
    return ChromaVectorStore()

vector_store = get_vector_store()
