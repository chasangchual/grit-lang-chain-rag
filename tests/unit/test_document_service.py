from uuid import uuid4

import pytest

from app.schemas.document import DocumentCreate, DocumentUpdate
from app.services.document import DocumentService


class TestDocumentService:
    """Unit tests for DocumentService."""

    def test_create_document(self, session):
        """Test creating a new document."""
        service = DocumentService(session)
        schema = DocumentCreate(
            hash="test_hash_123",
            extension="pdf",
            text="Test content",
            source="/test/path.pdf",
            meta={"author": "Test"},
        )

        document = service.create_document(schema)

        assert document.id is not None
        assert document.public_id is not None
        assert document.hash == "test_hash_123"
        assert document.extension == "pdf"
        assert document.text == "Test content"
        assert document.source == "/test/path.pdf"
        assert document.meta == {"author": "Test"}

    def test_get_document(self, session, sample_document):
        """Test getting a document by public ID."""
        service = DocumentService(session)

        result = service.get_document(sample_document.public_id)

        assert result is not None
        assert result.public_id == sample_document.public_id
        assert result.hash == sample_document.hash

    def test_get_document_not_found(self, session):
        """Test getting a non-existent document."""
        service = DocumentService(session)

        result = service.get_document(uuid4())

        assert result is None

    def test_get_document_by_hash(self, session, sample_document):
        """Test getting a document by hash."""
        service = DocumentService(session)

        result = service.get_document_by_hash(sample_document.hash)

        assert result is not None
        assert result.hash == sample_document.hash

    def test_list_documents(self, session, document_factory):
        """Test listing documents with pagination."""
        service = DocumentService(session)
        # Create multiple documents
        for i in range(5):
            document_factory(hash=f"hash_{i}")

        documents, total = service.list_documents(skip=0, limit=3)

        assert len(documents) == 3
        assert total == 5

    def test_list_documents_empty(self, session):
        """Test listing documents when none exist."""
        service = DocumentService(session)

        documents, total = service.list_documents()

        assert len(documents) == 0
        assert total == 0

    def test_update_document(self, session, sample_document):
        """Test updating a document."""
        service = DocumentService(session)
        schema = DocumentUpdate(
            text="Updated content",
            meta={"updated": True},
        )

        result = service.update_document(sample_document.public_id, schema)

        assert result is not None
        assert result.text == "Updated content"
        assert result.meta == {"updated": True}
        # Unchanged fields should remain
        assert result.hash == sample_document.hash
        assert result.extension == sample_document.extension

    def test_update_document_not_found(self, session):
        """Test updating a non-existent document."""
        service = DocumentService(session)
        schema = DocumentUpdate(text="Updated")

        result = service.update_document(uuid4(), schema)

        assert result is None

    def test_delete_document(self, session, sample_document):
        """Test deleting a document."""
        service = DocumentService(session)
        public_id = sample_document.public_id

        result = service.delete_document(public_id)

        assert result is True
        assert service.get_document(public_id) is None

    def test_delete_document_not_found(self, session):
        """Test deleting a non-existent document."""
        service = DocumentService(session)

        result = service.delete_document(uuid4())

        assert result is False

    def test_document_exists(self, session, sample_document):
        """Test checking if a document exists by hash."""
        service = DocumentService(session)

        assert service.document_exists(sample_document.hash) is True
        assert service.document_exists("nonexistent_hash") is False

    def test_get_document_with_embeddings(
        self, session, sample_document, embedding_factory
    ):
        """Test getting a document with its embeddings."""
        service = DocumentService(session)
        # Create embeddings for the document
        embedding_factory(document=sample_document, index=0)
        embedding_factory(document=sample_document, index=1)

        result = service.get_document_with_embeddings(sample_document.public_id)

        assert result is not None
        assert len(result.embeddings) == 2
