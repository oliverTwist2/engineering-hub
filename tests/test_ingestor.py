import pytest
from api.schemas import FilePayload
from workers.ingestor import describe_diagram_image, ingest_files, process_single_file

def test_describe_diagram_image() -> None:
    """Verifies vision description output for diagram image files.
    
    Parameters: none.
    Returns: None.
    """
    desc = describe_diagram_image("base64data", "arch.png")
    assert "arch.png" in desc

def test_process_single_file() -> None:
    """Verifies chunk generation and record parsing for a single text file payload.
    
    Parameters: none.
    Returns: None.
    """
    payload = FilePayload(path="test.py", content="def foo(): pass", type="py")
    records, skipped, err = process_single_file(payload, "proj1")
    assert err == ""
    assert skipped is False
    assert len(records) > 0
    assert records[0]["metadata"]["source_path"] == "test.py"

def test_ingest_files_batch() -> None:
    """Verifies batch ingestion processing of multiple files.
    
    Parameters: none.
    Returns: None.
    """
    files = [
        FilePayload(path="doc1.md", content="System architecture overview", type="md"),
        FilePayload(path="doc2.md", content="Database schema definition", type="md")
    ]
    resp = ingest_files(files, "proj1")
    assert resp.ingested == 2
    assert len(resp.errors) == 0
