import base64
import os
from typing import Tuple

SUPPORTED_TEXT_EXTS = {".md", ".txt", ".py", ".ts", ".js", ".go", ".yaml", ".yml", ".json"}
SUPPORTED_IMAGE_EXTS = {".png", ".jpg", ".jpeg"}
SUPPORTED_PDF_EXTS = {".pdf"}

def detect_file_type(file_path: str, hint_type: str = "") -> str:
    """Detects and normalizes the file type extension from file path or hint.
    
    Parameters:
        file_path: Path or filename of target file.
        hint_type: Optional explicitly provided file type hint.
    Returns:
        Normalized file extension string without leading dot (e.g. 'py', 'png').
    """
    if hint_type:
        return hint_type.lstrip(".").lower()
    _, ext = os.path.splitext(file_path)
    return ext.lstrip(".").lower() if ext else "txt"

def is_image_type(file_type: str) -> bool:
    """Checks whether the file type represents an architecture diagram image.
    
    Parameters:
        file_type: Normalized file type string.
    Returns:
        Boolean indicating if the file is a supported image format.
    """
    return f".{file_type.lower()}" in SUPPORTED_IMAGE_EXTS

def decode_content_if_base64(content: str) -> Tuple[bytes, bool]:
    """Attempts to decode a base64 encoded payload content string.
    
    Parameters:
        content: Raw content string or base64 encoded text.
    Returns:
        Tuple of (decoded_bytes, is_binary_success).
    """
    try:
        decoded = base64.b64decode(content, validate=True)
        return decoded, True
    except Exception:
        return content.encode("utf-8"), False

def parse_file_content(content: str, file_type: str) -> str:
    """Parses and extracts raw text from text, code, PDF, or structured files.
    
    Parameters:
        content: Raw string content or base64 encoded representation.
        file_type: Normalized file type string.
    Returns:
        Clean extracted text string for ingestion.
    """
    if is_image_type(file_type):
        return content  # Keep image content as base64 payload for vision processing
        
    bytes_data, is_base64 = decode_content_if_base64(content)
    if is_base64:
        return bytes_data.decode("utf-8", errors="ignore")
    return content
