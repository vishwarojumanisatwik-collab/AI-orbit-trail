from __future__ import annotations

import json
from pathlib import Path

from src.config import PROCESSED_DATA_DIR, RAW_DATA_DIR
from src.discovery.base import DiscoveredTool
from src.cleaning.candidates import filter_tool_candidates
from src.cleaning.deduplication import (
    canonical_tool_url,
    deduplicate_tools,
)


def build_clean_candidates() -> Path:
    """Build and save the cleaned AI tool candidate dataset."""

    input_path = Path(RAW_DATA_DIR) / "discovered_tools.json"
    output_path = Path(PROCESSED_DATA_DIR) / "tool_candidates.json"

    with input_path.open("r", encoding="utf-8") as file:
        raw_data = json.load(file)

    records = [
        DiscoveredTool.model_validate(item)
        for item in raw_data
    ]

    candidates = filter_tool_candidates(records)
    unique_tools = deduplicate_tools(candidates)

    cleaned_data = []

    for record in unique_tools:
        cleaned_data.append(
            {
                "name": record.name.strip(),
                "discovered_url": canonical_tool_url(
                    str(record.discovered_url)
                ),
                "source_name": record.source_name,
                "source_url": (
                    str(record.source_url)
                    if record.source_url
                    else None
                ),
            }
        )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(
            cleaned_data,
            file,
            indent=2,
            ensure_ascii=False,
        )

    return output_path


if __name__ == "__main__":
    output = build_clean_candidates()
    print(f"Saved cleaned candidates to: {output}")