from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class WebsiteEnrichment(BaseModel):
    """Structured information extracted from an official website."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    official_url: HttpUrl

    title: Optional[str] = None
    meta_description: Optional[str] = None
    og_description: Optional[str] = None

    headings: List[str] = Field(default_factory=list)
    paragraphs: List[str] = Field(default_factory=list)

    http_status: Optional[int] = None
    final_url: Optional[HttpUrl] = None
    extraction_status: str = "pending"