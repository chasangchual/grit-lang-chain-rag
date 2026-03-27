import os
from typing import Generator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.main import create_app
from app.api.deps import get_db
from app.models.base import Base
from app.models.document import Document
from app.models.embedding import Embedding


# Use SQLite in-memory for testing (without pgvector features)
# For full vector search tests, use a test PostgreSQL database with pgvector
SQLALCHEMY_TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///:memory:")

# Detect if we're using SQLite (no pgvector support)
USING_SQLITE = SQLALCHEMY_TEST_DATABASE_URL.startswith("sqlite")


def requires_pgvector(func):
    """Decorator to skip tests that require pgvector when using SQLite."""
    return pytest.mark.skipif(
        USING_SQLITE, reason="Vector search tests require PostgreSQL with pgvector"
    )(func)


@pytest.fixture(scope="function")
def engine():
    """Create a test database engine."""
    engine = create_engine(
        SQLALCHEMY_TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def session(engine) -> Generator[Session, None, None]:
    """Create a test database session with rollback."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
def client(session: Session) -> Generator[TestClient, None, None]:
    """Create a test client with overridden database dependency."""
    app = create_app()

    def override_get_db():
        try:
            yield session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


# Factory fixtures


@pytest.fixture
def document_factory(session: Session):
    """Factory for creating test documents."""

    def _create_document(
        hash: str | None = None,
        extension: str = "txt",
        text: str | None = "Test document content",
        source: str | None = "/test/path.txt",
        meta: dict | None = None,
    ) -> Document:
        doc = Document(
            public_id=uuid4(),
            hash=hash or f"hash_{uuid4().hex[:8]}",
            extension=extension,
            text=text,
            source=source,
            meta=meta,
        )
        session.add(doc)
        session.flush()
        return doc

    return _create_document


@pytest.fixture
def embedding_factory(session: Session, document_factory):
    """Factory for creating test embeddings."""

    def _create_embedding(
        document: Document | None = None,
        index: int = 0,
        text: str = "Test chunk content",
        vector: list[float] | None = None,
        meta: dict | None = None,
    ) -> Embedding:
        if document is None:
            document = document_factory()

        # Default vector (simplified for SQLite testing)
        if vector is None:
            vector = [0.1] * 1536

        emb = Embedding(
            public_id=uuid4(),
            doc_id=document.id,
            index=index,
            text=text,
            vector=vector,
            meta=meta,
        )
        session.add(emb)
        session.flush()
        return emb

    return _create_embedding


@pytest.fixture
def sample_document(document_factory) -> Document:
    """Create a sample document for testing."""
    return document_factory(
        hash="sample_hash_123",
        extension="pdf",
        text="This is a sample document for testing purposes.",
        source="/samples/test.pdf",
        meta={"author": "Test Author"},
    )


@pytest.fixture
def sample_embedding(embedding_factory, sample_document) -> Embedding:
    """Create a sample embedding for testing."""
    return embedding_factory(
        document=sample_document,
        index=0,
        text="This is a sample chunk from the document.",
        meta={"page": 1},
    )
