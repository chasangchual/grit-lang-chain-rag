from datetime import datetime, timezone
from uuid import uuid4

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import relationship

from .base import ExternalBase


def utc_now() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)


class Embedding(ExternalBase):
    __tablename__ = "embeddings"

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

    # Relationships
    document = relationship("Document", back_populates="embeddings")

    def __repr__(self):
        return f"<Embedding(id={self.id}, doc_id={self.doc_id}, index={self.index})>"
