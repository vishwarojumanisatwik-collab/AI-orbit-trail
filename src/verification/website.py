from __future__ import annotations

import re
from urllib.parse import urlparse

import httpx
from rapidfuzz.fuzz import ratio

from src.config import REQUEST_TIMEOUT, USER_AGENT
from src.verification.providers import provider_domain_matches


def _get_domain(url: str) -> str:
    """Return the normalized hostname."""

    hostname = (urlparse(url).hostname or "").lower()

    if hostname.startswith("www."):
        hostname = hostname[4:]

    return hostname


def _normalize_text(value: str) -> str:
    """Normalize text for entity comparison."""

    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", " ", value)

    return " ".join(value.split())


def domain_matches_entity(
    entity_name: str,
    url: str,
) -> bool:
    """
    Check whether the website domain plausibly matches
    the entity name.
    """

    domain = _get_domain(url)
    domain_name = domain.split(".")[0]

    normalized_entity = _normalize_text(entity_name)
    normalized_domain = _normalize_text(domain_name)

    if not normalized_entity or not normalized_domain:
        return False

    entity_compact = normalized_entity.replace(" ", "")
    domain_compact = normalized_domain.replace(" ", "")

    if domain_compact in entity_compact:
        return True

    if entity_compact in domain_compact:
        return True

    score = ratio(
        entity_compact,
        domain_compact,
    )

    return score >= 70


def check_website(url: str) -> dict:
    """
    Check whether a candidate official website is reachable.
    """

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": (
            "text/html,application/xhtml+xml,"
            "application/xml;q=0.9,*/*;q=0.8"
        ),
    }

    result = {
        "url": url,
        "domain": _get_domain(url),
        "status": None,
        "final_url": None,
        "reachable": False,
        "verification_status": "unverified",
        "notes": None,
    }

    try:
        with httpx.Client(
            timeout=REQUEST_TIMEOUT,
            follow_redirects=True,
            headers=headers,
        ) as client:

            response = client.get(url)

            result["status"] = response.status_code
            result["final_url"] = str(response.url)

            if response.status_code == 200:
                result["reachable"] = True
                result["verification_status"] = "reachable"
                result["notes"] = "Website returned HTTP 200."

            elif response.status_code in {
                301,
                302,
                307,
                308,
            }:
                result["reachable"] = True
                result["verification_status"] = "redirected"
                result["notes"] = "Website redirected."

            elif response.status_code in {
                401,
                403,
                429,
            }:
                result["verification_status"] = "blocked"
                result["notes"] = (
                    "Website appears to restrict automated access."
                )

            else:
                result["verification_status"] = "failed"
                result["notes"] = (
                    f"Unexpected HTTP status "
                    f"{response.status_code}."
                )

    except httpx.TimeoutException:
        result["verification_status"] = "timeout"
        result["notes"] = "Website request timed out."

    except httpx.RequestError as exc:
        result["verification_status"] = "error"
        result["notes"] = str(exc)

    return result


def verify_entity_website(
    entity_name: str,
    candidate_url: str,
) -> dict:
    """
    Combine technical reachability and entity/domain matching.

    Provider mappings are considered when the product name
    differs from the company/domain name.
    """

    result = check_website(candidate_url)

    technically_valid = result["verification_status"] in {
        "reachable",
        "redirected",
        "blocked",
    }

    if not technically_valid:
        result["verification_status"] = "failed"
        result["notes"] = (
            result["notes"]
            or "Website failed technical verification."
        )

        return result

    direct_match = domain_matches_entity(
        entity_name,
        candidate_url,
    )

    provider_match = provider_domain_matches(
        entity_name,
        candidate_url,
    )

    if direct_match or provider_match:
        result["verification_status"] = "verified"

        if provider_match and not direct_match:
            result["notes"] = (
                "Verified through known provider domain mapping."
            )
        else:
            result["notes"] = (
                "Verified through entity/domain matching."
            )

    else:
        result["verification_status"] = "manual_review"
        result["notes"] = (
            "Website is reachable but the domain does not "
            "clearly match the entity name or known provider."
        )

    return result