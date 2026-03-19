from datetime import datetime, timezone
from uuid import uuid4

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import relationship

from .base import Base


def utc_now() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)


class Embedding(Base):
    __tablename__ = "embeddings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    public_id = Column(UUID(as_uuid=True), default=uuid4, unique=True, nullable=False)
    doc_id = Column(
        Integer,
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    index = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    vector = Column(
        Vector(1536), nullable=False
    )  # 1536 dimensions for OpenAI embeddings
    meta = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    document = relationship("Document", back_populates="embeddings")

    def __repr__(self):
        return f"<Embedding(id={self.id}, doc_id={self.doc_id}, index={self.index})>"
