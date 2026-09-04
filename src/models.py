from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class Source(BaseModel):
    """Information about where the record was discovered."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    url: Optional[HttpUrl] = None


class Verification(BaseModel):
    """Verification results for canonical entity information."""

    model_config = ConfigDict(extra="forbid")

    website_verified: bool = False
    logo_verified: bool = False
    verification_notes: Optional[str] = None
    verified_at: Optional[datetime] = None


class ToolRecord(BaseModel):
    """
    Canonical AI Orbit Tool entity.

    This follows the common entity schema from the project specification
    and adds tool-specific metadata.
    """

    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    entity_type: str = "tool"

    name: str = Field(min_length=1)
    slug: str = Field(min_length=1)

    description: str = Field(min_length=1)

    url: HttpUrl
    logo_url: Optional[HttpUrl] = None

    categories: List[str] = Field(default_factory=list)

    company_name: Optional[str] = None

    pricing_model: Optional[str] = None
    platforms: List[str] = Field(default_factory=list)

    api_available: Optional[bool] = None
    open_source: Optional[bool] = None

    source: Source

    verification: Verification = Field(default_factory=Verification)

    description_generated: bool = False

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)