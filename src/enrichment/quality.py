from __future__ import annotations

from typing import Any


def classify_enrichment_quality(record: dict[str, Any]) -> str:
    """
    Classify the usefulness of official website extraction.

    rich:
        Sufficient authoritative content for LLM description generation.

    limited:
        Official site was reached, but extracted content is sparse.

    unavailable:
        Official site could not be extracted.
    """

    status = record.get("extraction_status")

    if status != "success":
        return "unavailable"

    title = (record.get("title") or "").strip()
    meta = (record.get("meta_description") or "").strip()
    headings = record.get("headings") or []
    paragraphs = record.get("paragraphs") or []

    if meta and (len(headings) >= 3 or len(paragraphs) >= 3):
        return "rich"

    if title and (meta or headings or paragraphs):
        return "limited"

    return "unavailable"