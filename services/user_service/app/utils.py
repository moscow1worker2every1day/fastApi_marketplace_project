"""Module for utils"""

from pathlib import Path


def _get_project_directory() -> Path:
    """Root directory of the service (for .env, alembic, keys)."""
    return Path(__file__).resolve().parent.parent


def _read_version() -> str:
    project_root = _get_project_directory()
    for path in (
        project_root / ".python-version",
        project_root.parent / ".python-version",
    ):
        if path.is_file():
            return path.read_text(encoding="utf-8").strip()
    return "unknown"
