"""
SQLAlchemy ORM models matching SYSTEM_DESIGN.md Section 5 (Database Schema).

Postgres is the source of truth for everything here; ChromaDB only stores
the embedding vectors themselves, keyed by `Chunk.id` (see Section 5's
"Embeddings Table (ChromaDB)" note on write order and consistency).
"""
import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    # Hashed API key only — the raw key is shown once at registration
    # (POST /api/v1/auth/register, Section 6) and never stored.
    api_key_hash = Column(String(255), unique=True, nullable=False)
    role = Column(String(20), nullable=False, default="user")  # 'user' | 'admin'
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    queries = relationship("Query", back_populates="user")


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    original_filename = Column(String(255), nullable=False)
    # Content hash, not filename hash — this is what powers dedup (FR-2):
    # the same file uploaded under a different name is still caught.
    file_hash = Column(String(64), unique=True, nullable=True)
    doc_type = Column(String(20), nullable=True)  # 'pdf' | 'docx' | 'txt' | 'md'
    source_url = Column(String(2048), nullable=True)
    total_chunks = Column(Integer, nullable=True)
    total_tokens = Column(Integer, nullable=True)
    status = Column(
        Enum("processing", "completed", "failed", name="document_status"),
        nullable=False,
        default="processing",
    )
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)

    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")


class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    char_start = Column(Integer, nullable=False)
    char_end = Column(Integer, nullable=False)
    token_count = Column(Integer, nullable=True)
    embedding_model = Column(String(255), nullable=True)
    embedding_dimension = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    document = relationship("Document", back_populates="chunks")

    # `id` is reused as ChromaDB's chunk_id (Section 5) — Postgres write
    # must land before the ChromaDB upsert, never after.


class Query(Base):
    __tablename__ = "queries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Nullable: a query can be logged even if auth is disabled
    # (security.enable_auth: false, Section 7) and there's no user to attach.
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    query_text = Column(Text, nullable=False)
    retrieved_chunks = Column(Integer, nullable=True)
    response = Column(Text, nullable=True)
    response_tokens = Column(Integer, nullable=True)
    generation_time_ms = Column(Integer, nullable=True)
    retrieval_time_ms = Column(Integer, nullable=True)
    total_time_ms = Column(Integer, nullable=True)
    # Average vector-similarity score of the chunks actually cited in the
    # answer — NOT the LLM's self-reported confidence. See Section 5.
    confidence_score = Column(Float, nullable=True)
    model_version = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="queries")
