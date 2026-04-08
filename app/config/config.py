from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Configurations(BaseSettings):
    app_name: str = "grit-rag"
    app_version: str = "0.1.0"
    app_env: str = "local"

    db_user: str = "postgres"
    db_password: str = "postgres"
    db_host: str = "localhost"
    db_port: str = "5432"
    db_name: str = "langchain_rag"

    redis_host: str = "localhost"
    redis_port: str = "6379"
    redis_password: str = ""
    redis_queue_instance: str = "0"
    redis_result_instance: str = "1"

    working_directory: Path = Path("/app/data")

    recursive: bool = False
    supported_extensions: list[str] = [
        ".txt",
        ".md",
        ".pdf",
        ".doc",
        ".docs",
        ".ppt",
        ".pptx",
        ".xls",
        ".xlsx",
    ]

    embedding_batch_size: int = 16

    @property
    def database_url(self) -> str:
        return f"postgresql+psycopg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}"

    @property
    def celery_broker_url(self) -> str:
        return f"{self.redis_url}/{self.redis_queue_instance}"

    @property
    def celery_result_backend(self) -> str:
        return f"{self.redis_url}/{self.redis_result_instance}"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


@lru_cache
def get_config() -> Configurations:
    return Configurations()
