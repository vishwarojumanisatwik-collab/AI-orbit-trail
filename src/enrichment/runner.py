from __future__ import annotations

import json
from pathlib import Path

from src.config import PROCESSED_DATA_DIR
from src.verification.registry import OFFICIAL_DOMAIN_REGISTRY
from src.enrichment.website import extract_official_website


def run_enrichment() -> None:
    input_path = Path(PROCESSED_DATA_DIR) / "tool_candidates.json"
    output_path = Path(PROCESSED_DATA_DIR) / "tool_enrichment.json"

    candidates = json.loads(
        input_path.read_text(encoding="utf-8")
    )

    results = []

    for candidate in candidates:
        name = candidate["name"]

        official_urls = OFFICIAL_DOMAIN_REGISTRY.get(name)

        if not official_urls:
            print(f"Skipping {name}: no official URL registered")
            continue

        official_url = official_urls[0]

        print(f"Enriching: {name}")
        print(f"  Official URL: {official_url}")

        enrichment = extract_official_website(
            name=name,
            official_url=official_url,
        )

        results.append(
            enrichment.model_dump(mode="json")
        )

        print(
            f"  Status: {enrichment.extraction_status}"
            f" | HTTP: {enrichment.http_status}"
        )

    output_path.write_text(
        json.dumps(
            results,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    successful = sum(
        1
        for record in results
        if record["extraction_status"] == "success"
    )

    print()
    print(f"Processed: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {len(results) - successful}")
    print()
    print(f"Saved to: {output_path}")


if __name__ == "__main__":
    run_enrichment()