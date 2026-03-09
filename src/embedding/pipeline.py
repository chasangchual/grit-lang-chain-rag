from __future__ import annotations

from pathlib import Path

from .config import PipelineConfig
from .discovery import FileDiscoveryService
from .embedders import EmbeddingProvider
from .loaders.base import LoaderRegistry
from .models import Chunk, Document, EmbeddedChunk
from .splitters import DocumentSplitter


class EmbeddingPipeline:
    def __init__(
        self,
        registry: LoaderRegistry,
        splitter: DocumentSplitter,
        embedder: EmbeddingProvider,
        discovery: FileDiscoveryService | None = None,
        config: PipelineConfig | None = None,
    ) -> None:
        self._registry = registry
        self._splitter = splitter
        self._embedder = embedder
        self._discovery = discovery or FileDiscoveryService()
        self._config = config or PipelineConfig()

    def process_directory(self, root_dir: Path) -> list[EmbeddedChunk]:
        files = self._discovery.list_files(root_dir=root_dir, recursive=self._config.recursive)
        supported = self._discovery.filter_supported(files, self._config.supported_extensions)
        return self.process_sources(supported)

    def process_sources(self, sources: list[str | Path]) -> list[EmbeddedChunk]:
        documents: list[Document] = []
        for source in sources:
            documents.extend(self._registry.load(source))

        chunks: list[Chunk] = []
        for document in documents:
            chunks.extend(self._splitter.split(document))

        return self._embed_chunks(chunks)

    def _embed_chunks(self, chunks: list[Chunk]) -> list[EmbeddedChunk]:
        if not chunks:
            return []

        embedded: list[EmbeddedChunk] = []
        batch_size = self._config.embedding_batch_size
        for start in range(0, len(chunks), batch_size):
            batch = chunks[start : start + batch_size]
            vectors = self._embedder.embed_texts([chunk.text for chunk in batch])
            if len(vectors) != len(batch):
                raise RuntimeError("Embedding provider returned mismatched vector count")

            embedded.extend(
                EmbeddedChunk(chunk=chunk, vector=vector)
                for chunk, vector in zip(batch, vectors, strict=True)
            )
        return embedded
