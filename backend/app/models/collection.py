"""
Collection models for organizing samples
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Collection(Base):
    """Collection model for organizing samples into hierarchical groups."""
    __tablename__ = "collections"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Basic info
    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)

    # Hierarchical structure
    parent_collection_id = Column(Integer, ForeignKey("collections.id"), nullable=True, index=True)

    # Smart collection configuration
    is_smart = Column(Boolean, default=False, index=True)
    smart_rules = Column(JSON, default=dict)  # Filtering rules for smart collections

    # Aggregated data
    sample_count = Column(Integer, default=0, server_default="0")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="collections")

    # Many-to-many with samples through association table
    samples = relationship(
        "Sample",
        secondary="collection_samples",
        back_populates="collections",
        lazy="selectin"
    )

    # Self-referential for nested collections
    sub_collections = relationship(
        "Collection",
        back_populates="parent_collection",
        remote_side=[parent_collection_id],
        cascade="all, delete-orphan"
    )
    parent_collection = relationship(
        "Collection",
        back_populates="sub_collections",
        remote_side=[id]
    )


class CollectionSample(Base):
    """Association table for collection-sample relationships with ordering."""
    __tablename__ = "collection_samples"

    __table_args__ = (
        UniqueConstraint("collection_id", "sample_id", name="uq_collection_sample"),
    )

    collection_id = Column(Integer, ForeignKey("collections.id", ondelete="CASCADE"), primary_key=True, index=True)
    sample_id = Column(Integer, ForeignKey("samples.id", ondelete="CASCADE"), primary_key=True, index=True)

    # Custom ordering within collection
    order = Column(Integer, default=0)

    # Timestamp
    added_at = Column(DateTime(timezone=True), server_default=func.now())
