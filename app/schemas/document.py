from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DocumentBase(BaseModel):
    """Base schema for Document with common fields."""

    hash: str = Field(
        ..., max_length=255, description="Document hash for deduplication"
    )
    extension: str = Field(
        ..., max_length=50, description="File extension (e.g., pdf, txt)"
    )
    text: str | None = Field(None, description="Extracted text content")
    source: str | None = Field(None, max_length=500, description="Source path or URL")
    meta: dict | None = Field(None, description="Additional metadata")


class DocumentCreate(DocumentBase):
    """Schema for creating a new document."""

    pass


class DocumentUpdate(BaseModel):
    """Schema for updating a document. All fields are optional."""

    hash: str | None = Field(None, max_length=255)
    extension: str | None = Field(None, max_length=50)
    text: str | None = None
    source: str | None = Field(None, max_length=500)
    meta: dict | None = None


class DocumentResponse(DocumentBase):
    """Schema for document response."""

    model_config = ConfigDict(from_attributes=True)

    public_id: UUID = Field(..., description="Public UUID identifier")
    created_at: datetime
    updated_at: datetime


class DocumentWithEmbeddingsResponse(DocumentResponse):
    """Schema for document response with embeddings count."""

    embeddings_count: int = Field(
        0, description="Number of embeddings for this document"
    )


class DocumentListResponse(BaseModel):
    """Schema for paginated document list response."""

    items: list[DocumentResponse]
    total: int = Field(..., description="Total number of documents")
    skip: int = Field(..., description="Number of items skipped")
    limit: int = Field(..., description="Maximum items per page")
