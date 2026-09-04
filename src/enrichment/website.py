from __future__ import annotations

import re
from typing import List

import httpx
from bs4 import BeautifulSoup

from src.config import REQUEST_TIMEOUT, USER_AGENT
from src.enrichment.models import WebsiteEnrichment


def _clean_text(value: str) -> str:
    """Normalize whitespace in extracted text."""
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def _extract_meta_content(
    soup: BeautifulSoup,
    *,
    name: str | None = None,
    property_name: str | None = None,
) -> str | None:
    if name:
        tag = soup.find("meta", attrs={"name": name})
    else:
        tag = soup.find("meta", attrs={"property": property_name})

    if not tag:
        return None

    content = tag.get("content")

    if not content:
        return None

    content = _clean_text(content)

    return content or None


def extract_official_website(
    name: str,
    official_url: str,
) -> WebsiteEnrichment:

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": (
            "text/html,application/xhtml+xml,"
            "application/xml;q=0.9,*/*;q=0.8"
        ),
    }

    try:
        with httpx.Client(
            timeout=REQUEST_TIMEOUT,
            follow_redirects=True,
            headers=headers,
        ) as client:

            response = client.get(official_url)

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")

        title = None

        if soup.title:
            title = _clean_text(
                soup.title.get_text(" ", strip=True)
            )

        meta_description = _extract_meta_content(
            soup,
            name="description",
        )

        og_description = _extract_meta_content(
            soup,
            property_name="og:description",
        )

        headings: List[str] = []

        for heading in soup.find_all(["h1", "h2", "h3"]):
            text = _clean_text(
                heading.get_text(" ", strip=True)
            )

            if text:
                headings.append(text)

        paragraphs: List[str] = []

        for paragraph in soup.find_all("p"):
            text = _clean_text(
                paragraph.get_text(" ", strip=True)
            )

            if text and len(text) >= 20:
                paragraphs.append(text)

        return WebsiteEnrichment(
            name=name,
            official_url=official_url,
            title=title,
            meta_description=meta_description,
            og_description=og_description,
            headings=headings,
            paragraphs=paragraphs,
            http_status=response.status_code,
            final_url=str(response.url),
            extraction_status="success",
        )

    except httpx.TimeoutException:
        return WebsiteEnrichment(
            name=name,
            official_url=official_url,
            extraction_status="timeout",
        )

    except httpx.HTTPStatusError as exc:
        return WebsiteEnrichment(
            name=name,
            official_url=official_url,
            http_status=exc.response.status_code,
            extraction_status="http_error",
        )

    except httpx.RequestError:
        return WebsiteEnrichment(
            name=name,
            official_url=official_url,
            extraction_status="request_error",
        )

    except Exception:
        return WebsiteEnrichment(
            name=name,
            official_url=official_url,
            extraction_status="error",
        )