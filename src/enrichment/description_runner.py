from __future__ import annotations

import json
import logging
from pathlib import Path

from src.config import PROCESSED_DATA_DIR
from src.enrichment.description_generator import DescriptionGenerator
from src.utils.logging import setup_logging


INPUT_FILE = Path(PROCESSED_DATA_DIR) / "tool_evidence.json"
OUTPUT_FILE = Path(PROCESSED_DATA_DIR) / "tool_descriptions.json"


def load_existing_results() -> dict[str, dict]:
    """Load previously generated results so the pipeline can resume safely."""

    if not OUTPUT_FILE.exists():
        return {}

    try:
        data = json.loads(
            OUTPUT_FILE.read_text(encoding="utf-8")
        )

        return {
            record["name"]: record
            for record in data
            if record.get("name")
        }

    except (json.JSONDecodeError, OSError):
        return {}


def save_results(results: list[dict]) -> None:
    """Persist results after each record."""

    OUTPUT_FILE.write_text(
        json.dumps(
            results,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def run_description_generation() -> None:
    logger = setup_logging()

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}"
        )

    data = json.loads(
        INPUT_FILE.read_text(encoding="utf-8")
    )

    existing = load_existing_results()

    generator = DescriptionGenerator()

    results = list(existing.values())

    logger.info(
        "Starting description generation for %d records",
        len(data),
    )

    for index, record in enumerate(data, start=1):
        name = record["name"]

        # Skip successfully completed records.
        if name in existing:
            previous = existing[name]

            if previous.get("description_generated") is True:
                logger.info(
                    "[%d/%d] Already generated: %s",
                    index,
                    len(data),
                    name,
                )
                continue

        logger.info(
            "[%d/%d] Processing: %s",
            index,
            len(data),
            name,
        )

        try:
            result = generator.generate(record)
            result_dict = result.model_dump(mode="json")

            # Replace previous result for this entity if necessary.
            results = [
                item
                for item in results
                if item.get("name") != name
            ]

            results.append(result_dict)
            existing[name] = result_dict

            save_results(results)

            logger.info(
                "Completed: %s | generated=%s",
                name,
                result_dict["description_generated"],
            )

        except Exception as exc:
            logger.exception(
                "Failed to generate description for %s: %s",
                name,
                exc,
            )

            # Preserve the failure instead of terminating the batch.
            failure = {
                "name": name,
                "description": "",
                "source_quality": record.get(
                    "source_quality",
                    "unknown",
                ),
                "generated_by": "openai",
                "model": generator.model,
                "description_generated": False,
                "error": str(exc),
            }

            results = [
                item
                for item in results
                if item.get("name") != name
            ]

            results.append(failure)
            existing[name] = failure

            save_results(results)

    generated = sum(
        1
        for record in results
        if record.get("description_generated") is True
    )

    unavailable = sum(
        1
        for record in results
        if not record.get("description")
    )

    logger.info("Description generation completed.")
    logger.info("Processed: %d", len(results))
    logger.info("Generated: %d", generated)
    logger.info("Without description: %d", unavailable)
    logger.info("Saved: %s", OUTPUT_FILE)

    print()
    print(f"Processed: {len(results)}")
    print(f"Generated: {generated}")
    print(f"Without description: {unavailable}")
    print(f"Saved: {OUTPUT_FILE}")


if __name__ == "__main__":
    run_description_generation()