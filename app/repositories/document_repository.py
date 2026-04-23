from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models.document import Document

from .base import BaseRepository


class DocumentRepository(BaseRepository[Document]):
    """Repository for Document model with specialized queries."""

    def __init__(self, session: Session):
        super().__init__(session, Document)

    def get_by_hash(self, hash: str) -> Document | None:
        """Get a document by its hash."""
        stmt = select(Document).where(Document.hash == hash)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_with_embeddings(self, public_id: UUID) -> Document | None:
        """Get a document with its embeddings eagerly loaded."""
        stmt = (
            select(Document)
            .options(joinedload(Document.embeddings))
            .where(Document.public_id == public_id)
        )
        return self.session.execute(stmt).unique().scalar_one_or_none()

    def get_with_embeddings_count(self, public_id: UUID) -> tuple[Document, int] | None:
        """Get a document with its embeddings count."""
        doc = self.get_by_public_id(public_id)
        if doc is None:
            return None
        count_stmt = (
            select(func.count())
            .select_from(Document.embeddings)
            .where(Document.public_id == public_id)
        )
        # Use the relationship to count
        count = len(doc.embeddings) if doc.embeddings else 0
        return doc, count

    def exists_by_hash(self, hash: str) -> bool:
        """Check if a document with the given hash exists."""
        stmt = select(func.count()).select_from(Document).where(Document.hash == hash)
        count = self.session.execute(stmt).scalar()
        return count > 0 if count else False
