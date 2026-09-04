from __future__ import annotations

import json
from pathlib import Path

from src.config import PROCESSED_DATA_DIR
from src.verification.logo import discover_logo_url, validate_logo_url
from src.verification.logo_registry import OFFICIAL_LOGO_REGISTRY
from src.verification.registry import OFFICIAL_DOMAIN_REGISTRY


def build_logo_candidates() -> Path:
    output_path = Path(PROCESSED_DATA_DIR) / "tool_logo_candidates.json"

    results = []

    for name, urls in OFFICIAL_DOMAIN_REGISTRY.items():
        official_url = urls[0]

        print(f"Checking logo: {name}")

        # Explicitly verified official logo overrides take priority.
        if name in OFFICIAL_LOGO_REGISTRY:
            logo_url = OFFICIAL_LOGO_REGISTRY[name]

            if validate_logo_url(logo_url):
                print(f"  Official override: {logo_url}")
            else:
                # Keep a previously verified official URL even if
                # the website temporarily rejects the request.
                print(
                    "  Registered official logo could not be "
                    "revalidated; keeping registry value."
                )

            results.append(
                {
                    "name": name,
                    "official_url": official_url,
                    "logo_url": logo_url,
                    "logo_verified": True,
                    "logo_source": "official_logo_registry",
                }
            )
            continue

        # Automatic discovery for entities without an explicit override.
        logo_url = discover_logo_url(official_url)

        results.append(
            {
                "name": name,
                "official_url": official_url,
                "logo_url": logo_url,
                "logo_verified": logo_url is not None,
                "logo_source": "official_website" if logo_url else None,
            }
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_text(
        json.dumps(results, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    verified = sum(
        1 for record in results
        if record["logo_verified"]
    )

    print()
    print(f"Saved {len(results)} logo candidates to:")
    print(output_path)
    print(f"Logo URLs discovered: {verified}/{len(results)}")

    return output_path


if __name__ == "__main__":
    build_logo_candidates()