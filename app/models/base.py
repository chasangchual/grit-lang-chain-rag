from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, DateTime, Integer
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4

def utc_now() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

class ExternalBase(Base):
    __abstract__ = True

    public_id = Column(UUID(as_uuid=True), default=uuid4, unique=True, nullable=False)
