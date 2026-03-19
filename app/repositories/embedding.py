from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.embedding import Embedding

from .base import BaseRepository


class EmbeddingRepository(BaseRepository[Embedding]):
    """Repository for Embedding model with vector search capabilities."""

    def __init__(self, session: Session):
        super().__init__(session, Embedding)

    def get_by_document_id(self, doc_id: int) -> list[Embedding]:
        """Get all embeddings for a document by internal document ID."""
        stmt = (
            select(Embedding)
            .where(Embedding.doc_id == doc_id)
            .order_by(Embedding.index)
        )
        return list(self.session.execute(stmt).scalars().all())

    def get_by_document_public_id(self, doc_public_id: UUID) -> list[Embedding]:
        """Get all embeddings for a document by public UUID."""
        stmt = (
            select(Embedding)
            .join(Document)
            .where(Document.public_id == doc_public_id)
            .order_by(Embedding.index)
        )
        return list(self.session.execute(stmt).scalars().all())

    def search_similar(
        self,
        query_vector: list[float],
        top_k: int = 10,
        threshold: float | None = None,
    ) -> list[tuple[Embedding, float]]:
        """
        Search for similar embeddings using cosine distance.

        Returns list of (Embedding, similarity_score) tuples ordered by similarity.
        Similarity score is 1 - cosine_distance, so higher is more similar.
        """
        # pgvector uses <=> for cosine distance (0 = identical, 2 = opposite)
        # We convert to similarity: 1 - (distance / 2) to get 0-1 range
        cosine_distance = Embedding.vector.cosine_distance(query_vector)
        similarity = 1 - (cosine_distance / 2)

        stmt = (
            select(Embedding, similarity.label("similarity"))
            .order_by(cosine_distance)
            .limit(top_k)
        )

        results = self.session.execute(stmt).all()

        # Filter by threshold if provided
        if threshold is not None:
            results = [(emb, sim) for emb, sim in results if sim >= threshold]

        return results

    def get_document_for_embedding(self, embedding: Embedding) -> Document | None:
        """Get the parent document for an embedding."""
        return embedding.document

    def create_for_document(
        self,
        doc_id: int,
        index: int,
        text: str,
        vector: list[float],
        meta: dict | None = None,
    ) -> Embedding:
        """Create an embedding for a specific document."""
        return self.create(
            doc_id=doc_id,
            index=index,
            text=text,
            vector=vector,
            meta=meta,
        )
