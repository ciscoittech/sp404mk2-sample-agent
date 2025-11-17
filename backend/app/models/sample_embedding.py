"""
Sample Embedding model for vector search.

Stores 1536-dimensional embeddings from text-embedding-3-small
as PostgreSQL float8 arrays for semantic similarity search.
For SQLite, uses JSON storage instead.
"""
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class SampleEmbedding(Base):
    """Vector embeddings for semantic search."""
    __tablename__ = "sample_embeddings"

    id = Column(Integer, primary_key=True, index=True)
    sample_id = Column(Integer, ForeignKey("samples.id"),
                      unique=True, nullable=False, index=True)
    # Use ARRAY for PostgreSQL, JSON for SQLite
    vibe_vector = Column(ARRAY(Float).with_variant(JSON, "sqlite"), nullable=False)  # 1536-dim float array
    embedding_source = Column(String)  # Source text used to generate embedding
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    sample = relationship("Sample", backref="embedding")
