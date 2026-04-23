from uuid import UUID

from sqlalchemy.orm import Session

from app.models.document import Document
from app.repositories.document_repository import D
from app.schemas.document import DocumentCreate, DocumentUpdate


class DocumentService:
    """Service layer for Document business logic."""

    def __init__(self, session: Session):
        self.session = session
        self.repository = DocumentService(session)

    def create_document(self, schema: DocumentCreate) -> Document:
        """Create a new document."""
        return self.repository.create(
            hash=schema.hash,
            extension=schema.extension,
            text=schema.text,
            source=schema.source,
            meta=schema.meta,
        )

    def get_document(self, public_id: UUID) -> Document | None:
        """Get a document by its public UUID."""
        return self.repository.get_by_public_id(public_id)

    def get_document_by_hash(self, hash: str) -> Document | None:
        """Get a document by its hash."""
        return self.repository.get_by_hash(hash)

    def list_documents(
        self, skip: int = 0, limit: int = 100
    ) -> tuple[list[Document], int]:
        """
        List documents with pagination.

        Returns tuple of (documents, total_count).
        """
        documents = self.repository.get_all(skip=skip, limit=limit)
        total = self.repository.count()
        return documents, total

    def update_document(
        self, public_id: UUID, schema: DocumentUpdate
    ) -> Document | None:
        """
        Update a document by its public UUID.

        Returns None if document not found.
        """
        document = self.repository.get_by_public_id(public_id)
        if document is None:
            return None

        update_data = schema.model_dump(exclude_unset=True)
        return self.repository.update(document, **update_data)

    def delete_document(self, public_id: UUID) -> bool:
        """
        Delete a document by its public UUID.

        Returns True if deleted, False if not found.
        """
        return self.repository.delete_by_public_id(public_id)

    def get_document_with_embeddings(self, public_id: UUID) -> Document | None:
        """Get a document with its embeddings eagerly loaded."""
        return self.repository.get_with_embeddings(public_id)

    def document_exists(self, hash: str) -> bool:
        """Check if a document with the given hash exists."""
        return self.repository.exists_by_hash(hash)
