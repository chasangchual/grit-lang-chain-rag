from uuid import uuid4

import pytest

from app.schemas.embedding import EmbeddingCreate, EmbeddingUpdate
from app.services.embedding import EmbeddingService


class TestEmbeddingService:
    """Unit tests for EmbeddingService."""

    def test_create_embedding(self, session, sample_document):
        """Test creating a new embedding."""
        service = EmbeddingService(session)
        schema = EmbeddingCreate(
            doc_public_id=sample_document.public_id,
            index=0,
            text="Test chunk content",
            vector=[0.1] * 1536,
            meta={"page": 1},
        )

        embedding = service.create_embedding(schema)

        assert embedding is not None
        assert embedding.id is not None
        assert embedding.public_id is not None
        assert embedding.doc_id == sample_document.id
        assert embedding.index == 0
        assert embedding.text == "Test chunk content"
        assert embedding.meta == {"page": 1}

    def test_create_embedding_document_not_found(self, session):
        """Test creating an embedding for a non-existent document."""
        service = EmbeddingService(session)
        schema = EmbeddingCreate(
            doc_public_id=uuid4(),
            index=0,
            text="Test chunk",
            vector=[0.1] * 1536,
        )

        result = service.create_embedding(schema)

        assert result is None

    def test_get_embedding(self, session, sample_embedding):
        """Test getting an embedding by public ID."""
        service = EmbeddingService(session)

        result = service.get_embedding(sample_embedding.public_id)

        assert result is not None
        assert result.public_id == sample_embedding.public_id
        assert result.text == sample_embedding.text

    def test_get_embedding_not_found(self, session):
        """Test getting a non-existent embedding."""
        service = EmbeddingService(session)

        result = service.get_embedding(uuid4())

        assert result is None

    def test_get_embeddings_by_document(
        self, session, sample_document, embedding_factory
    ):
        """Test getting all embeddings for a document."""
        service = EmbeddingService(session)
        # Create multiple embeddings
        embedding_factory(document=sample_document, index=0, text="Chunk 0")
        embedding_factory(document=sample_document, index=1, text="Chunk 1")
        embedding_factory(document=sample_document, index=2, text="Chunk 2")

        results = service.get_embeddings_by_document(sample_document.public_id)

        assert len(results) == 3
        # Should be ordered by index
        assert results[0].index == 0
        assert results[1].index == 1
        assert results[2].index == 2

    def test_get_embeddings_by_document_empty(self, session, sample_document):
        """Test getting embeddings for a document with no embeddings."""
        service = EmbeddingService(session)

        results = service.get_embeddings_by_document(sample_document.public_id)

        assert len(results) == 0

    def test_update_embedding(self, session, sample_embedding):
        """Test updating an embedding."""
        service = EmbeddingService(session)
        schema = EmbeddingUpdate(
            text="Updated chunk content",
            meta={"page": 2, "updated": True},
        )

        result = service.update_embedding(sample_embedding.public_id, schema)

        assert result is not None
        assert result.text == "Updated chunk content"
        assert result.meta == {"page": 2, "updated": True}
        # Unchanged fields should remain
        assert result.index == sample_embedding.index

    def test_update_embedding_not_found(self, session):
        """Test updating a non-existent embedding."""
        service = EmbeddingService(session)
        schema = EmbeddingUpdate(text="Updated")

        result = service.update_embedding(uuid4(), schema)

        assert result is None

    def test_delete_embedding(self, session, sample_embedding):
        """Test deleting an embedding."""
        service = EmbeddingService(session)
        public_id = sample_embedding.public_id

        result = service.delete_embedding(public_id)

        assert result is True
        assert service.get_embedding(public_id) is None

    def test_delete_embedding_not_found(self, session):
        """Test deleting a non-existent embedding."""
        service = EmbeddingService(session)

        result = service.delete_embedding(uuid4())

        assert result is False
