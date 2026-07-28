import json
from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.responses import StreamingResponse
from api.schemas import EvalSummaryResponse, IngestRequest, IngestResponse, QueryRequest, QueryResponse
from config import settings
from orchestrator.agent import process_rag_query
from storage.metadata_db import get_eval_summary
from workers.ingestor import ingest_files
from workers.retriever import hybrid_search, synthesise_answer_stream

router = APIRouter()

def verify_api_key(x_api_key: str = Header(None)) -> str:
    """Validates the incoming X-API-Key security header.
    
    Parameters:
        x_api_key: Header value supplied by client.
    Returns:
        Validated API key string.
    """
    if x_api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key. Check request headers."
        )
    return x_api_key

@router.post("/ingest", response_model=IngestResponse)
def ingest_documents(req: IngestRequest, api_key: str = Depends(verify_api_key)) -> IngestResponse:
    """Ingests a batch of files into the vector store.
    
    Parameters:
        req: IngestRequest body containing files list and project tag.
        api_key: Validated API key header.
    Returns:
        IngestResponse detailing ingested count and errors.
    """
    return ingest_files(req.files, req.project_tag)

def stream_query_events(req: QueryRequest):
    """Generates SSE stream events for natural language queries.
    
    Parameters:
        req: QueryRequest containing query string and project tag.
    Returns:
        Generator yielding text event strings.
    """
    chunks = hybrid_search(req.question, req.project_tag)
    for text_chunk in synthesise_answer_stream(req.question, chunks):
        yield f"data: {json.dumps({'content': text_chunk})}\n\n"
    final_resp = process_rag_query(req)
    data = {"answer": final_resp.answer, "citations": [c.dict() for c in final_resp.citations], "quality_score": final_resp.quality_score}
    yield f"data: {json.dumps(data)}\n\n"

@router.post("/query")
def query_documents(req: QueryRequest, api_key: str = Depends(verify_api_key)):
    """Executes a natural language RAG query returning JSON or SSE stream.
    
    Parameters:
        req: QueryRequest payload.
        api_key: Validated API key header.
    Returns:
        QueryResponse JSON or StreamingResponse SSE.
    """
    if req.stream:
        return StreamingResponse(stream_query_events(req), media_type="text/event-stream")
    return process_rag_query(req)

@router.get("/eval/summary", response_model=EvalSummaryResponse)
def evaluation_summary(api_key: str = Depends(verify_api_key)) -> EvalSummaryResponse:
    """Returns evaluation metrics summary logged across all queries.
    
    Parameters:
        api_key: Validated API key header.
    Returns:
        EvalSummaryResponse object containing telemetry statistics.
    """
    stats = get_eval_summary()
    return EvalSummaryResponse(**stats)
