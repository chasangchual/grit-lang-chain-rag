"""Backward-compatible entrypoint for splitter classes.

This file is intentionally kept with the current filename for compatibility.
Prefer importing from ``embedding.splitters`` in new code.
"""

from .splitters import DocumentSplitter, RecursiveTextSplitter

TextSplitter = RecursiveTextSplitter

__all__ = ["DocumentSplitter", "RecursiveTextSplitter", "TextSplitter"]
