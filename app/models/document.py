from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import relationship

from .base import Base


def utc_now() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    public_id = Column(UUID(as_uuid=True), default=uuid4, unique=True, nullable=False)
    hash = Column(String(255), nullable=False, index=True)
    extension = Column(String(50), nullable=False)
    text = Column(Text, nullable=True)
    source = Column(String(500), nullable=True)
    meta = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    embeddings = relationship(
        "Embedding", back_populates="document", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Document(id={self.id}, hash='{self.hash}', extension='{self.extension}')>"
