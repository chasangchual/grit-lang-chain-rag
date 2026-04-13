from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ChatMessage(BaseModel):
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, description="User query")
    top_k: int = Field(
        5, ge=1, le=20, description="Number of relevant chunks to retrieve"
    )
    conversation_history: list[ChatMessage] | None = Field(
        None, description="Previous conversation messages"
    )


class SourceChunk(BaseModel):
    document_id: UUID = Field(..., description="Document UUID")
    chunk_index: int = Field(..., description="Chunk index in document")
    content: str = Field(..., description="Chunk text content")
    similarity: float = Field(..., description="Similarity score")


class ChatResponse(BaseModel):
    answer: str = Field(..., description="Generated answer")
    sources: list[SourceChunk] = Field(
        default_factory=list, description="Source chunks used"
    )
    model: str = Field(..., description="LLM model used for generation")
