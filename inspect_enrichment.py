import json
from pathlib import Path

path = Path("data/processed/tool_enrichment.json")
data = json.loads(path.read_text(encoding="utf-8"))

print("Records:", len(data))
print()

for i, record in enumerate(data, start=1):
    print(
        f"{i}. {record['name']} | "
        f"{record['extraction_status']} | "
        f"title={record['title']!r} | "
        f"meta={record['meta_description']!r} | "
        f"headings={len(record['headings'])} | "
        f"paragraphs={len(record['paragraphs'])}"
    )
