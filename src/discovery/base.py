from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class DiscoveredTool(BaseModel):
    """
    Raw candidate discovered from an external source.

    Discovery records are not considered verified.
    Verification happens in a later pipeline stage.
    """

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    discovered_url: HttpUrl

    source_name: str = Field(min_length=1)
    source_url: Optional[HttpUrl] = None

    source_category: Optional[str] = None
    source_description: Optional[str] = None

    discovered_category: Optional[str] = None

    external_id: Optional[str] = None