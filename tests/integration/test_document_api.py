from uuid import uuid4

import pytest
from fastapi import status


class TestDocumentAPI:
    """Integration tests for Document API endpoints."""

    def test_create_document(self, client):
        """Test POST /api/v1/documents."""
        payload = {
            "hash": "test_hash_create",
            "extension": "pdf",
            "text": "Test document content",
            "source": "/test/path.pdf",
            "meta": {"author": "Test Author"},
        }

        response = client.post("/api/v1/documents", json=payload)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "public_id" in data
        assert data["hash"] == "test_hash_create"
        assert data["extension"] == "pdf"
        assert data["text"] == "Test document content"
        assert data["source"] == "/test/path.pdf"
        assert data["meta"] == {"author": "Test Author"}
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_document_minimal(self, client):
        """Test creating a document with minimal required fields."""
        payload = {
            "hash": "minimal_hash",
            "extension": "txt",
        }

        response = client.post("/api/v1/documents", json=payload)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["hash"] == "minimal_hash"
        assert data["extension"] == "txt"
        assert data["text"] is None
        assert data["source"] is None

    def test_list_documents(self, client, document_factory):
        """Test GET /api/v1/documents."""
        # Create test documents
        for i in range(5):
            document_factory(hash=f"list_hash_{i}")

        response = client.get("/api/v1/documents")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] == 5
        assert len(data["items"]) == 5

    def test_list_documents_pagination(self, client, document_factory):
        """Test pagination on document list."""
        for i in range(10):
            document_factory(hash=f"page_hash_{i}")

        response = client.get("/api/v1/documents?skip=0&limit=3")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) == 3
        assert data["total"] == 10
        assert data["skip"] == 0
        assert data["limit"] == 3

    def test_get_document(self, client, sample_document):
        """Test GET /api/v1/documents/{public_id}."""
        response = client.get(f"/api/v1/documents/{sample_document.public_id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["public_id"] == str(sample_document.public_id)
        assert data["hash"] == sample_document.hash

    def test_get_document_not_found(self, client):
        """Test getting a non-existent document."""
        fake_id = uuid4()

        response = client.get(f"/api/v1/documents/{fake_id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    def test_update_document(self, client, sample_document):
        """Test PATCH /api/v1/documents/{public_id}."""
        payload = {
            "text": "Updated document content",
            "meta": {"updated": True},
        }

        response = client.patch(
            f"/api/v1/documents/{sample_document.public_id}",
            json=payload,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["text"] == "Updated document content"
        assert data["meta"] == {"updated": True}
        # Unchanged fields should remain
        assert data["hash"] == sample_document.hash
        assert data["extension"] == sample_document.extension

    def test_update_document_not_found(self, client):
        """Test updating a non-existent document."""
        fake_id = uuid4()

        response = client.patch(
            f"/api/v1/documents/{fake_id}",
            json={"text": "Updated"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_document(self, client, sample_document):
        """Test DELETE /api/v1/documents/{public_id}."""
        response = client.delete(f"/api/v1/documents/{sample_document.public_id}")

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify deletion
        get_response = client.get(f"/api/v1/documents/{sample_document.public_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_document_not_found(self, client):
        """Test deleting a non-existent document."""
        fake_id = uuid4()

        response = client.delete(f"/api/v1/documents/{fake_id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_document_embeddings(self, client, sample_document, embedding_factory):
        """Test GET /api/v1/documents/{public_id}/embeddings."""
        # Create embeddings for the document
        embedding_factory(document=sample_document, index=0, text="Chunk 0")
        embedding_factory(document=sample_document, index=1, text="Chunk 1")

        response = client.get(
            f"/api/v1/documents/{sample_document.public_id}/embeddings"
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        assert data[0]["index"] == 0
        assert data[1]["index"] == 1

    def test_get_document_embeddings_not_found(self, client):
        """Test getting embeddings for a non-existent document."""
        fake_id = uuid4()

        response = client.get(f"/api/v1/documents/{fake_id}/embeddings")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "healthy"}
