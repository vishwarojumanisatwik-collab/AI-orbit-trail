from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from src.config import FINAL_DATA_DIR, PROCESSED_DATA_DIR
from src.enrichment.description_cleaner import normalize_known_description
from src.enrichment.official_fallbacks import OFFICIAL_DESCRIPTION_FALLBACKS
from src.final.classification import classify_tool
from src.verification.registry import OFFICIAL_DOMAIN_REGISTRY


CANDIDATES_FILE = Path(PROCESSED_DATA_DIR) / "tool_candidates.json"
EVIDENCE_FILE = Path(PROCESSED_DATA_DIR) / "tool_evidence.json"
DESCRIPTIONS_FILE = Path(PROCESSED_DATA_DIR) / "tool_descriptions.json"
LOGOS_FILE = Path(PROCESSED_DATA_DIR) / "tool_logo_candidates.json"

JSON_OUTPUT = Path(FINAL_DATA_DIR) / "ai_tools_final.json"
CSV_OUTPUT = Path(FINAL_DATA_DIR) / "ai_tools_final.csv"


def load_json(path: Path) -> list[dict[str, Any]]:
    """Load a JSON file containing a list of records."""

    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError(f"Expected a JSON list in {path}")

    return data


def index_by_name(
    records: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Create a case-insensitive lookup dictionary keyed by record name."""

    return {
        record["name"].strip().lower(): record
        for record in records
        if record.get("name")
    }


def build_description(
    name: str,
    evidence: dict[str, Any],
    generated: dict[str, Any],
) -> tuple[str, str]:
    """
    Return the best available factual description.

    Priority:
    1. Real LLM-generated description
    2. Official website description
    3. Official website paragraph
    4. Curated official-source fallback
    5. Empty value
    """

    # 1. Real LLM output.
    if generated.get("description_generated") is True:
        description = (
            generated.get("description") or ""
        ).strip()

        if description:
            return (
                normalize_known_description(
                    name,
                    description,
                ),
                "llm",
            )

    # 2. Official website metadata.
    official_description = (
        evidence.get("official_description") or ""
    ).strip()

    if official_description:
        cleaned = normalize_known_description(
            name,
            official_description,
        )

        if cleaned:
            return cleaned, "official_website"

    # 3. Official website paragraphs.
    paragraphs = evidence.get("paragraphs") or []

    for paragraph in paragraphs:
        paragraph = paragraph.strip()

        if len(paragraph) >= 30:
            cleaned = normalize_known_description(
                name,
                paragraph,
            )

            if cleaned:
                return cleaned, "official_website"

    # 4. Curated official-source fallback.
    fallback = OFFICIAL_DESCRIPTION_FALLBACKS.get(name)

    if fallback:
        description = (
            fallback.get("description") or ""
        ).strip()

        if description:
            cleaned = normalize_known_description(
                name,
                description,
            )

            if cleaned:
                return (
                    cleaned,
                    fallback.get(
                        "source",
                        "official_source_fallback",
                    ),
                )

    # 5. No usable evidence.
    return "", "unavailable"


def build_record(
    candidate: dict[str, Any],
    evidence: dict[str, Any],
    generated: dict[str, Any],
    logo: dict[str, Any],
) -> dict[str, Any]:
    """Build one normalized final AI tool record."""

    name = candidate["name"].strip()

    # Verified official URL.
    official_urls = OFFICIAL_DOMAIN_REGISTRY.get(name, [])

    official_url = (
        official_urls[0]
        if official_urls
        else candidate.get("discovered_url")
    )

    # Factual description.
    description, description_source = build_description(
        name=name,
        evidence=evidence,
        generated=generated,
    )

    # Deterministic ID.
    tool_id = (
        name.lower()
        .replace(" ", "-")
        .replace("|", "")
        .replace(".", "")
        .replace("/", "-")
    )

    # Evidence-based classification.
    categories = classify_tool(
        name=name,
        description=description,
        headings=evidence.get("headings") or [],
    )

    # ChatGPT uses an official OpenAI documentation fallback,
    # so the enrichment quality should not remain "unavailable".
    source_quality = evidence.get("source_quality")

    if (
        name == "ChatGPT"
        and description_source == "official_openai_documentation"
    ):
        source_quality = "official_fallback"

    return {
        "id": f"tool-{tool_id}",
        "entity_type": "tool",
        "name": name,
        "description": description,
        "url": official_url,
        "logo_url": logo.get("logo_url"),
        "categories": categories,

        "source_name": candidate.get("source_name"),
        "source_url": candidate.get("source_url"),

        "website_verified": True,
        "logo_verified": bool(logo.get("logo_verified")),
        "logo_source": logo.get("logo_source"),

        "description_generated": bool(
            generated.get("description_generated")
        ),
        "description_source": description_source,
        "source_quality": source_quality,

        "verification_notes": (
            "Official website selected from verified domain registry."
        ),
    }


def validate_record(
    record: dict[str, Any],
) -> list[str]:
    """Validate required fields in a final record."""

    errors: list[str] = []

    required_fields = [
        "id",
        "entity_type",
        "name",
        "description",
        "url",
        "source_name",
        "source_url",
    ]

    for field in required_fields:
        if not record.get(field):
            errors.append(
                f"Missing required field: {field}"
            )

    if record.get("entity_type") != "tool":
        errors.append(
            "entity_type must be 'tool'"
        )

    if record.get("website_verified") is not True:
        errors.append(
            "Website is not verified"
        )

    return errors


def assemble_dataset() -> list[dict[str, Any]]:
    """Assemble, clean, classify, validate, and save final dataset."""

    candidates = load_json(CANDIDATES_FILE)
    evidence = load_json(EVIDENCE_FILE)
    descriptions = load_json(DESCRIPTIONS_FILE)
    logos = load_json(LOGOS_FILE)

    evidence_by_name = index_by_name(evidence)
    descriptions_by_name = index_by_name(descriptions)
    logos_by_name = index_by_name(logos)

    final_records: list[dict[str, Any]] = []
    validation_errors: list[dict[str, Any]] = []

    for candidate in candidates:
        name = candidate["name"].strip()
        key = name.lower()

        evidence_record = evidence_by_name.get(
            key,
            {},
        )

        description_record = descriptions_by_name.get(
            key,
            {},
        )

        logo_record = logos_by_name.get(
            key,
            {},
        )

        record = build_record(
            candidate=candidate,
            evidence=evidence_record,
            generated=description_record,
            logo=logo_record,
        )

        errors = validate_record(record)

        if errors:
            validation_errors.append(
                {
                    "name": name,
                    "errors": errors,
                }
            )
            continue

        final_records.append(record)

    FINAL_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # JSON output.
    JSON_OUTPUT.write_text(
        json.dumps(
            final_records,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    # CSV output.
    dataframe = pd.DataFrame(
        final_records
    )

    dataframe.to_csv(
        CSV_OUTPUT,
        index=False,
        encoding="utf-8-sig",
    )

    print()
    print(
        "Final dataset assembly completed."
    )
    print(
        f"Input candidates: {len(candidates)}"
    )
    print(
        f"Final records: {len(final_records)}"
    )
    print(
        f"Validation failures: {len(validation_errors)}"
    )

    print()
    print(
        f"JSON: {JSON_OUTPUT}"
    )
    print(
        f"CSV:  {CSV_OUTPUT}"
    )

    if validation_errors:
        print()
        print("Validation errors:")

        for item in validation_errors:
            print(
                f"- {item['name']}: "
                f"{item['errors']}"
            )

    return final_records


if __name__ == "__main__":
    assemble_dataset()