from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from uuid import uuid4

from ..models import Document


class LoaderDependencyError(RuntimeError):
    pass


class DocumentLoader(ABC):
    @abstractmethod
    def supports(self, source: str | Path) -> bool:
        raise NotImplementedError

    @abstractmethod
    def load(self, source: str | Path) -> list[Document]:
        raise NotImplementedError


class LoaderRegistry:
    def __init__(self, loaders: list[DocumentLoader] | None = None) -> None:
        self._loaders: list[DocumentLoader] = loaders or []

    def register(self, loader: DocumentLoader) -> None:
        self._loaders.append(loader)

    def get_loader(self, source: str | Path) -> DocumentLoader:
        for loader in self._loaders:
            if loader.supports(source):
                return loader
        raise ValueError(f"No loader found for source: {source}")

    def load(self, source: str | Path) -> list[Document]:
        return self.get_loader(source).load(source)


def build_document(source: str | Path, doc_type: str, text: str, metadata: dict | None = None) -> Document:
    return Document(
        id=str(uuid4()),
        source=str(source),
        type=doc_type,
        text=text,
        metadata=metadata or {},
    )
