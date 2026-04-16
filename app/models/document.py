from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import relationship

from .base import ExternalBase


def utc_now() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)


class Document(ExternalBase):
    __tablename__ = "documents"

    hash = Column(String(255), nullable=False, index=True)
    extension = Column(String(50), nullable=False)
    text = Column(Text, nullable=True)
    source = Column(String(500), nullable=True)
    meta = Column(JSON, nullable=True)

    # Relationships
    embeddings = relationship(
        "Embedding", back_populates="document", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Document(id={self.id}, hash='{self.hash}', extension='{self.extension}')>"
