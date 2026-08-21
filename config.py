import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Central configuration settings loaded from environment variables."""
    anthropic_api_key: str = ""
    vector_backend: str = os.getenv("VECTOR_BACKEND", "chroma")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///hub.db")
    api_key: str = os.getenv("API_KEY", "your-hub-api-key")
    ingest_batch_size: int = int(os.getenv("INGEST_BATCH_SIZE", "10"))
    chunk_size: int = 512
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "64"))
    
    # Model Assignments
    model_orchestrator: str = os.getenv("MODEL_ORCHESTRATOR", "claude-3-opus-20240229")
    model_ingestor: str = os.getenv("MODEL_INGESTOR", "claude-3-5-haiku-20241022")
    model_retriever: str = os.getenv("MODEL_RETRIEVER", "claude-3-5-sonnet-20241022")
    model_test_writer: str = os.getenv("MODEL_TEST_WRITER", "claude-3-5-haiku-20241022")
    model_code_writer: str = os.getenv("MODEL_CODE_WRITER", "claude-3-5-haiku-20241022")

    model_config = SettingsConfigDict(env_file=".env")

def get_settings() -> Settings:
    """Returns a fresh instance of application settings.
    
    Parameters: none.
    Returns: Settings instance containing active configuration values.
    """
    return Settings()

settings = get_settings()
