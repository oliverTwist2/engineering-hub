import pytest
from utils.file_parser import detect_file_type, is_image_type, parse_file_content

def test_detect_file_type() -> None:
    """Verifies file type detection from extension and hint.
    
    Parameters: none.
    Returns: None.
    """
    assert detect_file_type("docs/architecture.png") == "png"
    assert detect_file_type("script.py") == "py"
    assert detect_file_type("unknown", hint_type="json") == "json"

def test_is_image_type() -> None:
    """Verifies detection of image extensions.
    
    Parameters: none.
    Returns: None.
    """
    assert is_image_type("png") is True
    assert is_image_type("jpg") is True
    assert is_image_type("py") is False

def test_parse_file_content_text() -> None:
    """Verifies text extraction returns clean raw string.
    
    Parameters: none.
    Returns: None.
    """
    content = "import os\nprint('hello')"
    parsed = parse_file_content(content, "py")
    assert parsed == content
