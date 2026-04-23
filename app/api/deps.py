from typing import Annotated, Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from app.config.db import SessionLocal
from app.services.document_service import DocumentService
from app.services.embedding_service import EmbeddingService


def get_db() -> Generator[Session, None, None]:
    """Dependency that provides a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Type alias for database session dependency
DbSession = Annotated[Session, Depends(get_db)]


def get_document_service(session: DbSession) -> DocumentService:
    """Dependency that provides a DocumentService instance."""
    return DocumentService(session)


def get_embedding_service(session: DbSession) -> EmbeddingService:
    """Dependency that provides an EmbeddingService instance."""
    return EmbeddingService(session)


# Type aliases for service dependencies
DocumentServiceDep = Annotated[DocumentService, Depends(get_document_service)]
EmbeddingServiceDep = Annotated[EmbeddingService, Depends(get_embedding_service)]
