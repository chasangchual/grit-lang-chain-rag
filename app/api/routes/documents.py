from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import DbSession, DocumentServiceDep, EmbeddingServiceDep
from app.schemas.document import (
    DocumentCreate,
    DocumentListResponse,
    DocumentResponse,
    DocumentUpdate,
)
from app.schemas.embedding import EmbeddingResponse

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post(
    "",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new document",
)
def create_document(
    schema: DocumentCreate,
    service: DocumentServiceDep,
    session: DbSession,
) -> DocumentResponse:
    """Create a new document."""
    document = service.create_document(schema)
    session.commit()
    return DocumentResponse.model_validate(document)


@router.get(
    "",
    response_model=DocumentListResponse,
    summary="List all documents",
)
def list_documents(
    service: DocumentServiceDep,
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum items to return"),
) -> DocumentListResponse:
    """List all documents with pagination."""
    documents, total = service.list_documents(skip=skip, limit=limit)
    return DocumentListResponse(
        items=[DocumentResponse.model_validate(doc) for doc in documents],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{public_id}",
    response_model=DocumentResponse,
    summary="Get a document by ID",
)
def get_document(
    public_id: UUID,
    service: DocumentServiceDep,
) -> DocumentResponse:
    """Get a document by its public UUID."""
    document = service.get_document(public_id)
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with id {public_id} not found",
        )
    return DocumentResponse.model_validate(document)


@router.patch(
    "/{public_id}",
    response_model=DocumentResponse,
    summary="Update a document",
)
def update_document(
    public_id: UUID,
    schema: DocumentUpdate,
    service: DocumentServiceDep,
    session: DbSession,
) -> DocumentResponse:
    """Partially update a document by its public UUID."""
    document = service.update_document(public_id, schema)
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with id {public_id} not found",
        )
    session.commit()
    return DocumentResponse.model_validate(document)


@router.delete(
    "/{public_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a document",
)
def delete_document(
    public_id: UUID,
    service: DocumentServiceDep,
    session: DbSession,
) -> None:
    """
    Delete a document by its public UUID.

    This will also delete all associated embeddings (cascade delete).
    """
    deleted = service.delete_document(public_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with id {public_id} not found",
        )
    session.commit()


@router.get(
    "/{public_id}/embeddings",
    response_model=list[EmbeddingResponse],
    summary="Get embeddings for a document",
)
def get_document_embeddings(
    public_id: UUID,
    document_service: DocumentServiceDep,
    embedding_service: EmbeddingServiceDep,
) -> list[EmbeddingResponse]:
    """Get all embeddings for a document."""
    # First check if document exists
    document = document_service.get_document(public_id)
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with id {public_id} not found",
        )

    embeddings = embedding_service.get_embeddings_by_document(public_id)
    return [
        EmbeddingResponse(
            public_id=emb.public_id,
            doc_public_id=document.public_id,
            index=emb.index,
            text=emb.text,
            meta=emb.meta,
            created_at=emb.created_at,
            updated_at=emb.updated_at,
        )
        for emb in embeddings
    ]
