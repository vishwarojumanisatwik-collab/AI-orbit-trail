from src.enrichment.quality import classify_enrichment_quality

import re
from typing import Any


NOISE_PATTERNS = [
    r"\bpricing\b",
    r"\bprice\b",
    r"\bper user\b",
    r"\$\d+",
    r"\bcredits?\b",
    r"\bfree to start\b",
    r"\bstart free\b",
    r"\bget started\b",
    r"\bread[y ]? to try\b",
    r"\bhassle[- ]?free\b",
    r"\b\d+%\s*off\b",
    r"\bno card\b",
    r"\bsubscription\b",
    r"©",
    r"\bcopyright\b",
    r"\bterms\b",
    r"\bprivacy\b",
    r"\bcookie\b",
    r"\bsign in\b",
    r"\blog in\b",
    r"\blogin\b",
    r"\blearn more\b",
    r"\bcontact us\b",
    r"\bcareers\b",
]


def _clean_text(value: str) -> str:
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def _is_noise(value: str) -> bool:
    text = _clean_text(value).lower()

    if not text:
        return True

    for pattern in NOISE_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            return True

    return False


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []

    for value in values:
        normalized = value.lower()

        if normalized in seen:
            continue

        seen.add(normalized)
        result.append(value)

    return result


def build_evidence(record: dict[str, Any]) -> dict[str, Any]:
    """
    Prepare authoritative website evidence for description generation.

    This function only cleans and selects information extracted
    from the official website. It does not infer new facts.
    """

    title = _clean_text(record.get("title") or "")
    meta = _clean_text(record.get("meta_description") or "")
    og_description = _clean_text(
        record.get("og_description") or ""
    )

    headings = [
        _clean_text(value)
        for value in (record.get("headings") or [])
        if value and not _is_noise(value)
    ]

    paragraphs = [
        _clean_text(value)
        for value in (record.get("paragraphs") or [])
        if value
        and not _is_noise(value)
        and len(_clean_text(value)) >= 30
    ]

    headings = _unique(headings)
    paragraphs = _unique(paragraphs)

    primary_description = meta or og_description

    return {
        "name": record["name"],
        "official_url": record["official_url"],
        "source_quality": classify_enrichment_quality(record),
        "title": title or None,
        "official_description": primary_description or None,
        "headings": headings,
        "paragraphs": paragraphs,
        "extraction_status": record.get("extraction_status"),
    }