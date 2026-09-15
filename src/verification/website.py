from __future__ import annotations

from urllib.parse import urlparse

import httpx

from src.config import REQUEST_TIMEOUT, USER_AGENT
from src.verification.providers import provider_domain_matches


def _get_domain(url: str) -> str:
    """Return the normalized hostname."""

    hostname = (urlparse(url).hostname or "").lower()

    if hostname.startswith("www."):
        hostname = hostname[4:]

    return hostname


def _normalize_text(value: str) -> str:
    """Normalize text for exact entity comparison."""

    value = value.lower().strip()

    result = []

    for char in value:
        if char.isalnum():
            result.append(char)

    return "".join(result)


def domain_matches_entity(
    entity_name: str,
    url: str,
) -> bool:
    """
    Check whether the root domain clearly matches the entity name.

    This deliberately avoids fuzzy matching because a similar-looking
    domain is not sufficient proof that a website is official.
    """

    domain = _get_domain(url)

    if not domain:
        return False

    domain_name = domain.split(".")[0]

    normalized_entity = _normalize_text(entity_name)
    normalized_domain = _normalize_text(domain_name)

    if not normalized_entity or not normalized_domain:
        return False

    return normalized_entity == normalized_domain


def check_website(url: str) -> dict:
    """
    Check whether a candidate website successfully responds.

    Redirects are followed so that verification can be performed
    against the final destination.
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
                401,
                403,
                429,
            }:
                result["verification_status"] = "blocked"
                result["notes"] = (
                    "Website restricts automated access. "
                    "Official verification is not possible."
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
    Perform strict official website verification.

    A website is verified only when:
    1. The final destination returns HTTP 200.
    2. The final domain clearly matches the entity name, or
       the entity has an explicitly known provider-domain mapping.

    Reachability alone is never treated as official verification.
    """

    result = check_website(candidate_url)

    if result["verification_status"] != "reachable":
        result["verification_status"] = "unverified"

        result["notes"] = (
            result["notes"]
            or "Website did not pass technical verification."
        )

        return result

    final_url = result["final_url"] or candidate_url

    direct_match = domain_matches_entity(
        entity_name,
        final_url,
    )

    provider_match = provider_domain_matches(
        entity_name,
        final_url,
    )

    if direct_match:
        result["verification_status"] = "verified"
        result["notes"] = (
            "Verified through exact entity/domain match."
        )

        return result

    if provider_match:
        result["verification_status"] = "verified"
        result["notes"] = (
            "Verified through known provider domain mapping."
        )

        return result

    result["verification_status"] = "manual_review"
    result["notes"] = (
        "Website is reachable, but the final domain does not "
        "clearly match the entity and no known provider mapping exists."
    )

    return result