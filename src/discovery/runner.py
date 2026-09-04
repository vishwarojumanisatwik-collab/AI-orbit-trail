from __future__ import annotations

import asyncio
from pathlib import Path

import orjson

from src.config import DISCOVERY_SOURCES, RAW_DATA_DIR
from src.discovery.directory import DirectoryDiscovery
from src.utils.logging import setup_logging
from src.utils.paths import ensure_directories


async def run_discovery() -> None:
    logger = setup_logging()
    ensure_directories()

    all_records = []

    for source in DISCOVERY_SOURCES:
        logger.info(
            "Starting discovery from %s",
            source["name"],
        )

        discovery = DirectoryDiscovery(
            source_name=source["name"],
            source_url=source["url"],
        )

        try:
            records = await discovery.discover()

            logger.info(
                "Discovered %d candidates from %s",
                len(records),
                source["name"],
            )

            all_records.extend(records)

        except Exception as exc:
            logger.exception(
                "Discovery failed for %s: %s",
                source["name"],
                exc,
            )

    output_path = Path(RAW_DATA_DIR) / "discovered_tools.json"

    data = [
        record.model_dump(mode="json")
        for record in all_records
    ]

    output_path.write_bytes(
        orjson.dumps(
            data,
            option=orjson.OPT_INDENT_2,
        )
    )

    logger.info(
        "Saved %d raw candidates to %s",
        len(data),
        output_path,
    )


if __name__ == "__main__":
    asyncio.run(run_discovery())