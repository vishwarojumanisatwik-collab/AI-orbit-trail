from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class VerifiedTool(BaseModel):
    """
    Tool candidate after official website verification.

    Verification is deliberately separated from discovery because
    a directory URL is not necessarily the official website.
    """

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)

    discovered_url: HttpUrl

    official_url: Optional[HttpUrl] = None

    official_domain: Optional[str] = None

    verification_status: str = "pending"

    verification_method: Optional[str] = None

    http_status: Optional[int] = None

    final_url: Optional[HttpUrl] = None

    verification_notes: Optional[str] = None