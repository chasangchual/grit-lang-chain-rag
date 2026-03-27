import os

from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from app.config.db import DATABASE_URL 

# Database configuration from environment variables
REDIS_USER = os.getenv("REDIS_USER", "postgres")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "postgres")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_QUEUE_INSTANCE = os.getenv("REDIS_INSTANCE", "0")
REDIS_RESULT_INSTANCE = os.getenv("REDIS_INSTANCE", "1")

REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}"

class Configurations(BaseSettings):
    app_name: str = "grit-rag"
    app_version: str = "0.1.0"
    app_env: str = "local"
    
    
    database_url: str = DATABASE_URL


    celery_broker_url: str = f"{REDIS_URL}/{REDIS_QUEUE_INSTANCE}"
    celery_result_backend: str = f"{REDIS_URL}/{REDIS_RESULT_INSTANCE}"
    
    working_directory: Path = Path("/app/data")
    
    
    # File discovery settings
    recursive: bool = False
    supported_extensions: list[str] = [".txt", ".md", ".pdf", ".doc", ".docs", ".ppt", ".pptx", ".xls", ".xlsx"]

    # Embedding settings
    embedding_batch_size: int = 16

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    
    
@lru_cache
def get_config() -> Configurations:
    return Configurations()