import json
from pathlib import Path

from src.enrichment.quality import classify_enrichment_quality

path = Path("data/processed/tool_enrichment.json")
data = json.loads(path.read_text(encoding="utf-8"))

counts = {
    "rich": 0,
    "limited": 0,
    "unavailable": 0,
}

for record in data:
    quality = classify_enrichment_quality(record)
    counts[quality] += 1

    print(
        f"{record['name']} | "
        f"{record['extraction_status']} | "
        f"{quality}"
    )

print()
print("QUALITY SUMMARY")
print("Rich:", counts["rich"])
print("Limited:", counts["limited"])
print("Unavailable:", counts["unavailable"])
