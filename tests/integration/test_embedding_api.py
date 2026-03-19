from uuid import uuid4

import pytest
from fastapi import status

from tests.conftest import requires_pgvector


class TestEmbeddingAPI:
    """Integration tests for Embedding API endpoints."""

    def test_create_embedding(self, client, sample_document):
        """Test POST /api/v1/embeddings."""
        payload = {
            "doc_public_id": str(sample_document.public_id),
            "index": 0,
            "text": "Test chunk content",
            "vector": [0.1] * 1536,
            "meta": {"page": 1},
        }

        response = client.post("/api/v1/embeddings", json=payload)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "public_id" in data
        assert data["doc_public_id"] == str(sample_document.public_id)
        assert data["index"] == 0
        assert data["text"] == "Test chunk content"
        assert data["meta"] == {"page": 1}
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_embedding_document_not_found(self, client):
        """Test creating an embedding for a non-existent document."""
        fake_doc_id = uuid4()
        payload = {
            "doc_public_id": str(fake_doc_id),
            "index": 0,
            "text": "Test chunk",
            "vector": [0.1] * 1536,
        }

        response = client.post("/api/v1/embeddings", json=payload)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    def test_get_embedding(self, client, sample_embedding):
        """Test GET /api/v1/embeddings/{public_id}."""
        response = client.get(f"/api/v1/embeddings/{sample_embedding.public_id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["public_id"] == str(sample_embedding.public_id)
        assert data["text"] == sample_embedding.text
        assert data["index"] == sample_embedding.index

    def test_get_embedding_not_found(self, client):
        """Test getting a non-existent embedding."""
        fake_id = uuid4()

        response = client.get(f"/api/v1/embeddings/{fake_id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_embedding(self, client, sample_embedding):
        """Test PATCH /api/v1/embeddings/{public_id}."""
        payload = {
            "text": "Updated chunk content",
            "meta": {"page": 2, "updated": True},
        }

        response = client.patch(
            f"/api/v1/embeddings/{sample_embedding.public_id}",
            json=payload,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["text"] == "Updated chunk content"
        assert data["meta"] == {"page": 2, "updated": True}
        # Unchanged fields should remain
        assert data["index"] == sample_embedding.index

    def test_update_embedding_not_found(self, client):
        """Test updating a non-existent embedding."""
        fake_id = uuid4()

        response = client.patch(
            f"/api/v1/embeddings/{fake_id}",
            json={"text": "Updated"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_embedding(self, client, sample_embedding):
        """Test DELETE /api/v1/embeddings/{public_id}."""
        response = client.delete(f"/api/v1/embeddings/{sample_embedding.public_id}")

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify deletion
        get_response = client.get(f"/api/v1/embeddings/{sample_embedding.public_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_embedding_not_found(self, client):
        """Test deleting a non-existent embedding."""
        fake_id = uuid4()

        response = client.delete(f"/api/v1/embeddings/{fake_id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @requires_pgvector
    def test_search_embeddings(self, client, sample_document, embedding_factory):
        """Test POST /api/v1/embeddings/search."""
        # Create test embeddings
        embedding_factory(document=sample_document, index=0, text="Chunk 0")
        embedding_factory(document=sample_document, index=1, text="Chunk 1")

        payload = {
            "query_vector": [0.1] * 1536,
            "top_k": 5,
        }

        response = client.post("/api/v1/embeddings/search", json=payload)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "results" in data
        assert "query_vector_dim" in data
        assert data["query_vector_dim"] == 1536

    @requires_pgvector
    def test_search_embeddings_with_threshold(
        self, client, sample_document, embedding_factory
    ):
        """Test search with similarity threshold."""
        embedding_factory(document=sample_document, index=0)

        payload = {
            "query_vector": [0.1] * 1536,
            "top_k": 10,
            "threshold": 0.5,
        }

        response = client.post("/api/v1/embeddings/search", json=payload)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "results" in data

    @requires_pgvector
    def test_search_embeddings_empty(self, client):
        """Test search when no embeddings exist."""
        payload = {
            "query_vector": [0.1] * 1536,
            "top_k": 10,
        }

        response = client.post("/api/v1/embeddings/search", json=payload)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["results"]) == 0

    def test_create_embedding_validation_error(self, client, sample_document):
        """Test validation error on invalid embedding data."""
        payload = {
            "doc_public_id": str(sample_document.public_id),
            "index": -1,  # Invalid: must be >= 0
            "text": "Test chunk",
            "vector": [0.1] * 1536,
        }

        response = client.post("/api/v1/embeddings", json=payload)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_cascade_delete(self, client, sample_document, embedding_factory):
        """Test that deleting a document cascades to its embeddings."""
        # Create embeddings
        emb1 = embedding_factory(document=sample_document, index=0)
        emb2 = embedding_factory(document=sample_document, index=1)

        # Delete the document
        response = client.delete(f"/api/v1/documents/{sample_document.public_id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify embeddings are also deleted
        response1 = client.get(f"/api/v1/embeddings/{emb1.public_id}")
        response2 = client.get(f"/api/v1/embeddings/{emb2.public_id}")
        assert response1.status_code == status.HTTP_404_NOT_FOUND
        assert response2.status_code == status.HTTP_404_NOT_FOUND
