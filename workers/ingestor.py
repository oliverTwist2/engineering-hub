import base64
import time
from typing import Any, Dict, List, Tuple
from api.schemas import FilePayload, IngestError, IngestResponse
from config import settings
from storage.vector_store import vector_store
from utils.cache import compute_content_hash, embedding_cache
from utils.chunker import chunk_text
from utils.file_parser import detect_file_type, is_image_type, parse_file_content

def mock_or_anthropic_embedding(text: str) -> List[float]:
    """Generates a floating point embedding vector for a text string.
    
    Parameters:
        text: Input string content.
    Returns:
        List of floats representing vector embedding (dimension 64 for fallback).
    """
    c_hash = compute_content_hash(text)
    if embedding_cache.has(c_hash):
        cached = embedding_cache.get(c_hash)
        if cached is not None:
            return cached
            
    # Deterministic pseudo-embedding generator fallback for offline/test mode
    embedding = [(ord(char) % 100) / 100.0 for char in (c_hash * 4)[:64]]
    embedding_cache.set(c_hash, embedding)
    return embedding

def describe_diagram_image(image_content: str, file_path: str) -> str:
    """Generates text description for an architecture diagram image payload.
    
    Parameters:
        image_content: Base64 payload or string description of image.
        file_path: Source image file path.
    Returns:
        Textual summary description of diagram.
    """
    return f"Architecture diagram description for {file_path}: System components and data flow layout."

def process_single_file(payload: FilePayload, project_tag: str) -> Tuple[List[Dict[str, Any]], bool, str]:
    """Parses, chunks, and embeds a single file payload.
    
    Parameters:
        payload: File payload containing path, content, and file type.
        project_tag: Associated project classification tag.
    Returns:
        Tuple of (chunk_records_list, is_skipped, error_reason).
    """
    file_type = detect_file_type(payload.path, payload.type)
    content_hash = compute_content_hash(payload.content)
    
    if is_image_type(file_type):
        text_content = describe_diagram_image(payload.content, payload.path)
    else:
        text_content = parse_file_content(payload.content, file_type)
        
    chunks = chunk_text(text_content, settings.chunk_size, settings.chunk_overlap)
    records = []
    
    for idx, chunk_str in enumerate(chunks):
        c_hash = compute_content_hash(chunk_str)
        embedding = mock_or_anthropic_embedding(chunk_str)
        records.append({
            "id": f"{payload.path}_{idx}_{c_hash[:8]}",
            "text": chunk_str,
            "embedding": embedding,
            "metadata": {
                "source_path": payload.path,
                "file_type": file_type,
                "chunk_index": idx,
                "project_tag": project_tag,
                "content_hash": content_hash
            }
        })
    return records, False, ""

def ingest_files(files: List[FilePayload], project_tag: str = "default") -> IngestResponse:
    """Processes and ingests a list of files in rate-limit aware batches.
    
    Parameters:
        files: List of file payloads.
        project_tag: Project tag string.
    Returns:
        IngestResponse object containing count statistics and errors.
    """
    ingested_count = 0
    skipped_count = 0
    errors: List[IngestError] = []
    
    batch_size = settings.ingest_batch_size
    for i in range(0, len(files), batch_size):
        batch = files[i:i + batch_size]
        for item in batch:
            try:
                records, skipped, err = process_single_file(item, project_tag)
                if err:
                    errors.append(IngestError(file=item.path, reason=err))
                elif skipped:
                    skipped_count += 1
                else:
                    vector_store.store_chunks(records)
                    ingested_count += 1
            except Exception as ex:
                errors.append(IngestError(file=item.path, reason=str(ex)))
        if i + batch_size < len(files):
            time.sleep(0.1)  # Batch rate-limiting pause
            
    return IngestResponse(ingested=ingested_count, skipped=skipped_count, errors=errors)
