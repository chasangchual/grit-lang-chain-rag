from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class EmbeddingBase(BaseModel):
    """Base schema for Embedding with common fields."""

    index: int = Field(..., ge=0, description="Chunk index within the document")
    text: str = Field(..., description="Text content of the chunk")
    meta: dict | None = Field(None, description="Additional metadata")


class EmbeddingCreate(EmbeddingBase):
    """Schema for creating a new embedding."""

    doc_public_id: UUID = Field(..., description="Public UUID of the parent document")
    vector: list[float] = Field(
        ..., min_length=1, max_length=4096, description="Embedding vector"
    )


class EmbeddingUpdate(BaseModel):
    """Schema for updating an embedding. All fields are optional."""

    index: int | None = Field(None, ge=0)
    text: str | None = None
    vector: list[float] | None = Field(None, min_length=1, max_length=4096)
    meta: dict | None = None


class EmbeddingResponse(EmbeddingBase):
    """Schema for embedding response."""

    model_config = ConfigDict(from_attributes=True)

    public_id: UUID = Field(..., description="Public UUID identifier")
    doc_public_id: UUID = Field(..., description="Public UUID of the parent document")
    created_at: datetime
    updated_at: datetime


class EmbeddingWithVectorResponse(EmbeddingResponse):
    """Schema for embedding response including the vector."""

    vector: list[float] = Field(..., description="Embedding vector")


class EmbeddingSearchRequest(BaseModel):
    """Schema for vector similarity search request."""

    query_vector: list[float] = Field(
        ..., min_length=1, max_length=4096, description="Query embedding vector"
    )
    top_k: int = Field(10, ge=1, le=100, description="Number of results to return")
    threshold: float | None = Field(
        None, ge=0.0, le=1.0, description="Minimum similarity threshold (0-1)"
    )


class EmbeddingSearchResult(BaseModel):
    """Schema for a single search result."""

    model_config = ConfigDict(from_attributes=True)

    public_id: UUID
    doc_public_id: UUID
    index: int
    text: str
    meta: dict | None
    similarity: float = Field(..., description="Cosine similarity score (0-1)")


class EmbeddingSearchResponse(BaseModel):
    """Schema for search results response."""

    results: list[EmbeddingSearchResult]
    query_vector_dim: int = Field(..., description="Dimension of the query vector")
