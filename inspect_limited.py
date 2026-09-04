import json
from pathlib import Path

data = json.loads(
    Path("data/processed/tool_evidence.json").read_text(encoding="utf-8")
)

for record in data:
    if record["source_quality"] != "rich":
        print("\n" + "=" * 70)
        print("NAME:", record["name"])
        print("QUALITY:", record["source_quality"])
        print("OFFICIAL URL:", record["official_url"])
        print("OFFICIAL DESCRIPTION:", record["official_description"])
        print("HEADINGS:", record["headings"])
        print("PARAGRAPHS:", record["paragraphs"])
