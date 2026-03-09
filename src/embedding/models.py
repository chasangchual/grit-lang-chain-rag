from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Document:
    """Normalized document object used across the ingestion pipeline."""

    id: str
    source: str
    type: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class Chunk:
    """A chunk generated from a source document."""

    id: str
    document_id: str
    index: int
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class EmbeddedChunk:
    """A chunk plus its embedding vector."""

    chunk: Chunk
    vector: list[float]
