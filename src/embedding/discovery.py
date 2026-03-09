from __future__ import annotations

from pathlib import Path


class FileDiscoveryService:
    def list_files(self, root_dir: Path, recursive: bool = True) -> list[Path]:
        if not root_dir.exists():
            raise FileNotFoundError(f"Directory does not exist: {root_dir}")
        if not root_dir.is_dir():
            raise NotADirectoryError(f"Expected a directory: {root_dir}")

        if recursive:
            return sorted(path for path in root_dir.rglob("*") if path.is_file())
        return sorted(path for path in root_dir.iterdir() if path.is_file())

    def filter_supported(self, files: list[Path], allowed_exts: set[str]) -> list[Path]:
        lowered = {ext.lower() for ext in allowed_exts}
        return [path for path in files if path.suffix.lower() in lowered]
