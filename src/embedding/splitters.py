from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import uuid4

from langchain_text_splitters import RecursiveCharacterTextSplitter

from .models import Chunk, Document


class DocumentSplitter(ABC):
    @abstractmethod
    def split(self, doc: Document) -> list[Chunk]:
        raise NotImplementedError


class RecursiveTextSplitter(DocumentSplitter):
    def __init__(self, chunk_size: int = 1200, chunk_overlap: int = 200) -> None:
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    def split(self, doc: Document) -> list[Chunk]:
        pieces = self._splitter.split_text(doc.text)
        return [
            Chunk(
                id=str(uuid4()),
                document_id=doc.id,
                index=idx,
                text=chunk_text,
                metadata={**doc.metadata, "source": doc.source, "type": doc.type},
            )
            for idx, chunk_text in enumerate(pieces)
        ]
