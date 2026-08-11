"""Module for utils"""

from pathlib import Path


def _get_project_directory() -> Path:
    """Root directory of the service (for .env, alembic, keys)."""
    return Path(__file__).resolve().parent.parent
