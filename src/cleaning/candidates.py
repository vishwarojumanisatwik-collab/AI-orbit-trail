from __future__ import annotations

from typing import Iterable, List
from urllib.parse import urlparse

from src.discovery.base import DiscoveredTool


def _domain(url: str) -> str:
    """Return hostname without www."""
    hostname = (urlparse(url).hostname or "").lower()

    if hostname.startswith("www."):
        hostname = hostname[4:]

    return hostname


def _normalized_path(url: str) -> str:
    """Return normalized URL path."""
    path = urlparse(url).path.strip().lower().rstrip("/")
    return path or "/"


def is_tool_candidate(record: DiscoveredTool) -> bool:
    """
    Determine whether a discovered record represents an individual
    AI tool page in the selected AI Tools module.

    Discovery uses positive URL matching rather than broad
    blacklist-based filtering.
    """

    url = str(record.discovered_url)

    domain = _domain(url)
    path = _normalized_path(url)

    # For the selected AI Tools module, individual tool pages
    # on There's An AI For That follow the /ai/<slug>/ pattern.
    if domain != "theresanaiforthat.com":
        return False

    if not path.startswith("/ai/"):
        return False

    # Must contain an actual tool slug after /ai/.
    slug = path[len("/ai/"):].strip("/")

    if not slug:
        return False

    # Reject paths that contain additional navigation levels.
    if "/" in slug:
        return False

    return True


def filter_tool_candidates(
    records: Iterable[DiscoveredTool],
) -> List[DiscoveredTool]:
    """Filter raw discovery results into AI tool candidates."""

    return [
        record
        for record in records
        if is_tool_candidate(record)
    ]