from __future__ import annotations

from typing import List
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from src.config import REQUEST_TIMEOUT, USER_AGENT
from src.discovery.base import DiscoveredTool


class DirectoryDiscovery:
    """
    Discover candidate AI tools from a directory page.

    This stage only discovers candidates.
    It does not verify that URLs are official.
    """

    def __init__(self, source_name: str, source_url: str) -> None:
        self.source_name = source_name
        self.source_url = source_url

    async def discover(self) -> List[DiscoveredTool]:
        headers = {
            "User-Agent": USER_AGENT,
        }

        async with httpx.AsyncClient(
            timeout=REQUEST_TIMEOUT,
            follow_redirects=True,
            headers=headers,
        ) as client:
            response = await client.get(self.source_url)
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")

        discovered: List[DiscoveredTool] = []

        for link in soup.find_all("a", href=True):
            name = link.get_text(" ", strip=True)
            href = link.get("href")

            if not name or not href:
                continue

            absolute_url = urljoin(self.source_url, href)

            if not absolute_url.startswith(("http://", "https://")):
                continue

            try:
                record = DiscoveredTool(
                    name=name,
                    discovered_url=absolute_url,
                    source_name=self.source_name,
                    source_url=self.source_url,
                )

                discovered.append(record)

            except Exception:
                continue

        return discovered