from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class PipelineConfig:
    recursive: bool = True
    chunk_size: int = 1200
    chunk_overlap: int = 200
    embedding_batch_size: int = 32
    text_encoding: str = "utf-8"
    supported_extensions: set[str] = field(
        default_factory=lambda: {
            ".txt",
            ".md",
            ".rst",
            ".pdf",
            ".docx",
            ".xlsx",
            ".xls",
            ".pptx",
        }
    )
