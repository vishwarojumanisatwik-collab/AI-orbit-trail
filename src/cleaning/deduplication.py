from __future__ import annotations

from typing import Iterable, List
from urllib.parse import urlparse

from src.discovery.base import DiscoveredTool


def canonical_tool_url(url: str) -> str:
    """
    Create a canonical URL for an AI tool.

    Tracking/query parameters are removed so that multiple
    links to the same tool become one record.
    """

    parsed = urlparse(str(url))

    hostname = (parsed.hostname or "").lower()

    if hostname.startswith("www."):
        hostname = hostname[4:]

    path = parsed.path.rstrip("/")

    return f"https://{hostname}{path}/"


def deduplicate_tools(
    records: Iterable[DiscoveredTool],
) -> List[DiscoveredTool]:
    """
    Deduplicate discovered tools using their canonical URL.

    The first occurrence is retained.
    """

    unique_tools: dict[str, DiscoveredTool] = {}

    for record in records:
        canonical_url = canonical_tool_url(
            str(record.discovered_url)
        )

        if canonical_url not in unique_tools:
            unique_tools[canonical_url] = record

    return list(unique_tools.values())