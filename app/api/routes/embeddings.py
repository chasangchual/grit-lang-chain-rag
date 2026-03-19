from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.api.deps import DbSession, EmbeddingServiceDep
from app.schemas.embedding import (
    EmbeddingCreate,
    EmbeddingResponse,
    EmbeddingSearchRequest,
    EmbeddingSearchResponse,
    EmbeddingUpdate,
)

router = APIRouter(prefix="/embeddings", tags=["embeddings"])


@router.post(
    "",
    response_model=EmbeddingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new embedding",
)
def create_embedding(
    schema: EmbeddingCreate,
    service: EmbeddingServiceDep,
    session: DbSession,
) -> EmbeddingResponse:
    """Create a new embedding for a document."""
    embedding = service.create_embedding(schema)
    if embedding is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with id {schema.doc_public_id} not found",
        )
    session.commit()
    return EmbeddingResponse(
        public_id=embedding.public_id,
        doc_public_id=embedding.document.public_id,
        index=embedding.index,
        text=embedding.text,
        meta=embedding.meta,
        created_at=embedding.created_at,
        updated_at=embedding.updated_at,
    )


@router.get(
    "/{public_id}",
    response_model=EmbeddingResponse,
    summary="Get an embedding by ID",
)
def get_embedding(
    public_id: UUID,
    service: EmbeddingServiceDep,
) -> EmbeddingResponse:
    """Get an embedding by its public UUID."""
    embedding = service.get_embedding(public_id)
    if embedding is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Embedding with id {public_id} not found",
        )
    return EmbeddingResponse(
        public_id=embedding.public_id,
        doc_public_id=embedding.document.public_id,
        index=embedding.index,
        text=embedding.text,
        meta=embedding.meta,
        created_at=embedding.created_at,
        updated_at=embedding.updated_at,
    )


@router.patch(
    "/{public_id}",
    response_model=EmbeddingResponse,
    summary="Update an embedding",
)
def update_embedding(
    public_id: UUID,
    schema: EmbeddingUpdate,
    service: EmbeddingServiceDep,
    session: DbSession,
) -> EmbeddingResponse:
    """Partially update an embedding by its public UUID."""
    embedding = service.update_embedding(public_id, schema)
    if embedding is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Embedding with id {public_id} not found",
        )
    session.commit()
    return EmbeddingResponse(
        public_id=embedding.public_id,
        doc_public_id=embedding.document.public_id,
        index=embedding.index,
        text=embedding.text,
        meta=embedding.meta,
        created_at=embedding.created_at,
        updated_at=embedding.updated_at,
    )


@router.delete(
    "/{public_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an embedding",
)
def delete_embedding(
    public_id: UUID,
    service: EmbeddingServiceDep,
    session: DbSession,
) -> None:
    """Delete an embedding by its public UUID."""
    deleted = service.delete_embedding(public_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Embedding with id {public_id} not found",
        )
    session.commit()


@router.post(
    "/search",
    response_model=EmbeddingSearchResponse,
    summary="Search similar embeddings",
)
def search_embeddings(
    request: EmbeddingSearchRequest,
    service: EmbeddingServiceDep,
) -> EmbeddingSearchResponse:
    """
    Search for similar embeddings using vector similarity.

    Returns embeddings ordered by similarity score (highest first).
    The similarity score ranges from 0 to 1, where 1 is identical.
    """
    results = service.search_similar(
        query_vector=request.query_vector,
        top_k=request.top_k,
        threshold=request.threshold,
    )
    return EmbeddingSearchResponse(
        results=results,
        query_vector_dim=len(request.query_vector),
    )
