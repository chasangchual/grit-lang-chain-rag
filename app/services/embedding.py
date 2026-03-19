from uuid import UUID

from sqlalchemy.orm import Session

from app.models.embedding import Embedding
from app.repositories.document import DocumentRepository
from app.repositories.embedding import EmbeddingRepository
from app.schemas.embedding import (
    EmbeddingCreate,
    EmbeddingSearchResult,
    EmbeddingUpdate,
)


class EmbeddingService:
    """Service layer for Embedding business logic."""

    def __init__(self, session: Session):
        self.session = session
        self.repository = EmbeddingRepository(session)
        self.document_repository = DocumentRepository(session)

    def create_embedding(self, schema: EmbeddingCreate) -> Embedding | None:
        """
        Create a new embedding.

        Returns None if the parent document is not found.
        """
        # Resolve document public_id to internal id
        document = self.document_repository.get_by_public_id(schema.doc_public_id)
        if document is None:
            return None

        return self.repository.create_for_document(
            doc_id=document.id,
            index=schema.index,
            text=schema.text,
            vector=schema.vector,
            meta=schema.meta,
        )

    def get_embedding(self, public_id: UUID) -> Embedding | None:
        """Get an embedding by its public UUID."""
        return self.repository.get_by_public_id(public_id)

    def get_embeddings_by_document(self, doc_public_id: UUID) -> list[Embedding]:
        """Get all embeddings for a document."""
        return self.repository.get_by_document_public_id(doc_public_id)

    def update_embedding(
        self, public_id: UUID, schema: EmbeddingUpdate
    ) -> Embedding | None:
        """
        Update an embedding by its public UUID.

        Returns None if embedding not found.
        """
        embedding = self.repository.get_by_public_id(public_id)
        if embedding is None:
            return None

        update_data = schema.model_dump(exclude_unset=True)
        return self.repository.update(embedding, **update_data)

    def delete_embedding(self, public_id: UUID) -> bool:
        """
        Delete an embedding by its public UUID.

        Returns True if deleted, False if not found.
        """
        return self.repository.delete_by_public_id(public_id)

    def search_similar(
        self,
        query_vector: list[float],
        top_k: int = 10,
        threshold: float | None = None,
    ) -> list[EmbeddingSearchResult]:
        """
        Search for similar embeddings using vector similarity.

        Returns list of EmbeddingSearchResult ordered by similarity (highest first).
        """
        results = self.repository.search_similar(
            query_vector=query_vector,
            top_k=top_k,
            threshold=threshold,
        )

        return [
            EmbeddingSearchResult(
                public_id=embedding.public_id,
                doc_public_id=embedding.document.public_id,
                index=embedding.index,
                text=embedding.text,
                meta=embedding.meta,
                similarity=similarity,
            )
            for embedding, similarity in results
        ]
