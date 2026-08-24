"""
Content-hash based duplicate detection (FR-2, SYSTEM_DESIGN.md Section 5's
documents.file_hash). Hashes the raw file bytes - not the parsed text - so
the same PDF re-uploaded under a different filename is still caught before
it's parsed, chunked, or re-embedded.
"""
import hashlib
from pathlib import Path

from sqlalchemy.orm import Session

from src.database.models import Document


def compute_file_hash(data: bytes) -> str:
    """SHA-256 hex digest (64 hex chars - matches documents.file_hash VARCHAR(64))."""
    return hashlib.sha256(data).hexdigest()


def compute_file_hash_from_path(path: str | Path) -> str:
    return compute_file_hash(Path(path).read_bytes())


def find_existing_document(session: Session, file_hash: str) -> Document | None:
    """Returns the existing Document with this file_hash, or None if it's new."""
    return session.query(Document).filter_by(file_hash=file_hash).one_or_none()
