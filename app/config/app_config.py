from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class AppConfig(BaseSettings):
    app_name: str = "grit-rag"
    app_version: str = "0.1.0"
    app_env: str = Field(default="local", validation_alias="APP_ENV")

    db_host: str = Field(default="localhost", validation_alias="POSTGRES_HOST")
    db_port: str = Field(default="5432", validation_alias="POSTGRES_PORT")
    db_name: str = Field(default="rag", validation_alias="POSTGRES_DB")
    db_user: str = Field(default="postgres", validation_alias="POSTGRES_USER")
    db_password: str = Field(
        default="yourpassword", validation_alias="POSTGRES_PASSWORD"
    )

    redis_host: str = Field(default="localhost", validation_alias="REDIS_HOST")
    redis_port: str = Field(default="6379", validation_alias="REDIS_PORT")
    redis_password: str = Field(default="", validation_alias="REDIS_PASSWORD")
    redis_queue_instance: str = Field(
        default="0", validation_alias="REDIS_QUEUE_INSTANCE"
    )
    redis_result_instance: str = Field(
        default="1", validation_alias="REDIS_RESULT_INSTANCE"
    )

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
        return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}"

    @property
    def celery_broker_url(self) -> str:
        return f"{self.redis_url}/{self.redis_queue_instance}"

    @property
    def celery_result_backend(self) -> str:
        return f"{self.redis_url}/{self.redis_result_instance}"

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_config() -> AppConfig:
    return AppConfig()
