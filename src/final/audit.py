from __future__ import annotations

import json
from pathlib import Path


FINAL_FILE = Path("data/final/ai_tools_final.json")


def main() -> None:
    if not FINAL_FILE.exists():
        raise FileNotFoundError(
            f"Final dataset not found: {FINAL_FILE}"
        )

    data = json.loads(
        FINAL_FILE.read_text(encoding="utf-8")
    )

    print("=== DATA QUALITY AUDIT ===")
    print(f"Records: {len(data)}")

    print(
        "Missing descriptions:",
        sum(not record.get("description") for record in data),
    )

    print(
        "Missing official URLs:",
        sum(not record.get("url") for record in data),
    )

    print(
        "Unverified websites:",
        sum(
            record.get("website_verified") is not True
            for record in data
        ),
    )

    print(
        "Missing logos:",
        sum(not record.get("logo_url") for record in data),
    )

    print(
        "Unverified logos:",
        sum(
            record.get("logo_verified") is not True
            for record in data
        ),
    )

    print(
        "LLM generated:",
        sum(
            record.get("description_generated") is True
            for record in data
        ),
    )

    print(
        "Official-source descriptions:",
        sum(
            record.get("description_source")
            == "official_website"
            for record in data
        ),
    )

    print(
        "Fallback descriptions:",
        sum(
            "fallback"
            in (record.get("description_source") or "")
            or record.get("description_source")
            == "official_openai_documentation"
            for record in data
        ),
    )

    print(
        "Empty categories:",
        sum(
            not record.get("categories")
            for record in data
        ),
    )

    print()
    print("=== TOOLS WITHOUT LOGOS ===")

    tools_without_logos = [
        record["name"]
        for record in data
        if not record.get("logo_url")
    ]

    if tools_without_logos:
        for name in tools_without_logos:
            print(f"- {name}")
    else:
        print("None")

    print()
    print("=== DESCRIPTION QUALITY ===")

    for record in data:
        name = record["name"]
        quality = record.get("source_quality")
        source = record.get("description_source")
        description = record.get("description")

        print()
        print(f"Tool: {name}")
        print(f"Quality: {quality}")
        print(f"Source: {source}")
        print(f"Description: {description}")


if __name__ == "__main__":
    main()