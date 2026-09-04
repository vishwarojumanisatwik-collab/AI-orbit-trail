from __future__ import annotations

from typing import Optional
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from src.config import REQUEST_TIMEOUT, USER_AGENT


def _absolute_url(base_url: str, value: str) -> str:
    """Convert a relative asset URL into an absolute URL."""
    return urljoin(base_url, value.strip())


def _candidate_urls(
    website_url: str,
    html: str,
    final_url: str,
) -> list[str]:
    """
    Extract official-site image candidates in priority order.

    Priority:
    1. favicon/icon
    2. apple touch icon
    3. Open Graph image
    4. Twitter image
    5. /favicon.ico
    """

    soup = BeautifulSoup(html, "lxml")

    candidates: list[str] = []

    # ---------------------------------------------------------
    # 1. Standard favicon / icon declarations
    # ---------------------------------------------------------

    for link in soup.find_all("link", href=True):
        rel_values = link.get("rel", [])

        if isinstance(rel_values, str):
            rel_values = rel_values.split()

        normalized_rel = {
            value.lower()
            for value in rel_values
        }

        if normalized_rel & {
            "icon",
            "shortcut",
            "apple-touch-icon",
            "apple-touch-icon-precomposed",
        }:
            candidates.append(
                _absolute_url(
                    final_url,
                    link["href"],
                )
            )

    # ---------------------------------------------------------
    # 2. Open Graph image
    # ---------------------------------------------------------

    for meta in soup.find_all(
        "meta",
        attrs={"property": "og:image"},
    ):
        content = meta.get("content")

        if content:
            candidates.append(
                _absolute_url(
                    final_url,
                    content,
                )
            )

    # ---------------------------------------------------------
    # 3. Twitter image
    # ---------------------------------------------------------

    for meta in soup.find_all(
        "meta",
        attrs={"name": "twitter:image"},
    ):
        content = meta.get("content")

        if content:
            candidates.append(
                _absolute_url(
                    final_url,
                    content,
                )
            )

    # ---------------------------------------------------------
    # 4. Standard browser fallback
    # ---------------------------------------------------------

    candidates.append(
        _absolute_url(
            final_url,
            "/favicon.ico",
        )
    )

    # Remove duplicate URLs while preserving order.
    return list(dict.fromkeys(candidates))


def validate_logo_url(url: str) -> bool:
    """
    Validate that a candidate URL returns an image resource.

    GET is used instead of relying on HEAD because many modern
    websites/CDNs do not implement HEAD consistently.
    """

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": (
            "image/avif,image/webp,image/png,"
            "image/jpeg,image/svg+xml,image/*,*/*;q=0.8"
        ),
    }

    try:
        with httpx.Client(
            timeout=REQUEST_TIMEOUT,
            follow_redirects=True,
            headers=headers,
        ) as client:

            response = client.get(url)

            if response.status_code >= 400:
                return False

            content_type = (
                response.headers
                .get("content-type", "")
                .lower()
            )

            return content_type.startswith("image/")

    except httpx.HTTPError:
        return False

    except Exception:
        return False

def discover_logo_url(
    website_url: str,
) -> Optional[str]:
    """
    Discover an official image asset from the website.
    """

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

            response = client.get(website_url)
            response.raise_for_status()

            final_url = str(response.url)

            candidates = _candidate_urls(
                website_url=website_url,
                html=response.text,
                final_url=final_url,
            )

            for candidate in candidates:
                if validate_logo_url(candidate):
                    return candidate

    except httpx.HTTPError:
        return None

    except Exception:
        return None

    return None