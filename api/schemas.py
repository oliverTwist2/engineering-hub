from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class FilePayload(BaseModel):
    """Payload representing a single file to ingest.
    
    Attributes:
        path: Relative or absolute path identifier.
        content: Raw text content or base64 encoded binary content.
        type: Detected or specified file extension/type.
    """
    path: str
    content: str
    type: str

class IngestRequest(BaseModel):
    """Request body for batch file ingestion.
    
    Attributes:
        files: List of file payloads to be processed.
        project_tag: Optional tag classifying the target project.
    """
    files: List[FilePayload]
    project_tag: str = Field(default="default", description="Project classification tag")

class IngestError(BaseModel):
    """Error record for a failed file ingestion attempt.
    
    Attributes:
        file: Path of the file that failed ingestion.
        reason: Explanation of the error encountered.
    """
    file: str
    reason: str

class IngestResponse(BaseModel):
    """Response body returning batch ingestion statistics.
    
    Attributes:
        ingested: Number of files successfully stored.
        skipped: Number of unchanged files skipped due to cache hit.
        errors: Detailed list of file ingestion failures.
    """
    ingested: int
    skipped: int
    errors: List[IngestError]

class QueryRequest(BaseModel):
    """Request body for natural language RAG queries.
    
    Attributes:
        question: User query string.
        project_tag: Optional filter for searching specific project chunks.
        stream: Whether to stream the response via Server-Sent Events.
    """
    question: str
    project_tag: Optional[str] = None
    stream: bool = False

class Citation(BaseModel):
    """Citation reference back to the source file chunk.
    
    Attributes:
        source: Source file path or filename.
        chunk: Zero-based or one-based index of the referenced chunk.
    """
    source: str
    chunk: int

class QueryResponse(BaseModel):
    """Response body containing answer, citations, and evaluation score.
    
    Attributes:
        answer: Synthesised markdown answer.
        citations: List of source chunk citations.
        quality_score: Evaluated quality score from 0.0 to 10.0.
    """
    answer: str
    citations: List[Citation]
    quality_score: float

class EvalSummaryResponse(BaseModel):
    """Response body summarizing system evaluation telemetry.
    
    Attributes:
        total_queries: Total number of queries logged.
        avg_quality: Average quality score across all logged queries.
        low_quality_queries: List of query strings that scored below threshold.
        source_coverage: Dictionary mapping filenames to citation counts.
    """
    total_queries: int
    avg_quality: float
    low_quality_queries: List[str]
    source_coverage: Dict[str, int]
