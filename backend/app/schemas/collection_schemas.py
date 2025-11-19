"""
Pydantic schemas for collections
"""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class SmartRulesSchema(BaseModel):
    """Smart collection filtering rules."""
    genres: list[str] | None = None
    bpm_min: float | None = None
    bpm_max: float | None = None
    tags: list[str] | None = None
    min_confidence: int | None = Field(None, ge=0, le=100)
    sample_types: list[str] | None = None


class CollectionCreate(BaseModel):
    """Schema for creating a collection."""
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    parent_collection_id: int | None = None
    is_smart: bool = False
    smart_rules: SmartRulesSchema | None = None


class CollectionUpdate(BaseModel):
    """Schema for updating a collection."""
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    parent_collection_id: int | None = None
    is_smart: bool | None = None
    smart_rules: SmartRulesSchema | None = None


class CollectionResponse(BaseModel):
    """Schema for collection responses."""
    id: int
    user_id: int
    name: str
    description: str | None
    parent_collection_id: int | None
    is_smart: bool
    smart_rules: dict[str, Any] | None
    sample_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SampleInCollectionResponse(BaseModel):
    """Schema for samples in a collection."""
    id: int
    title: str
    genre: str | None
    bpm: float | None
    duration: float | None
    added_at: datetime

    class Config:
        from_attributes = True


class CollectionDetailResponse(CollectionResponse):
    """Schema for detailed collection with samples and sub-collections."""
    samples: list[SampleInCollectionResponse] | None = None
    sub_collections: list[CollectionResponse] | None = None


class AddSamplesRequest(BaseModel):
    """Request schema for adding samples to a collection."""
    sample_ids: list[int] = Field(..., min_length=1)


class CollectionListResponse(BaseModel):
    """Response schema for paginated collection list."""
    items: list[CollectionResponse]
    total: int
