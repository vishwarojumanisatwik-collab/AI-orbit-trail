from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = BASE_DIR / "data" / "raw" / "bulk_source_models.csv"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "bulk_models_cleaned.csv"
REPORT_FILE = BASE_DIR / "data" / "processed" / "bulk_models_cleaning_report.txt"


# Discovery/provider platforms.
# These URLs may be useful as references, but they are NOT automatically
# treated as the model creator's official website.
THIRD_PARTY_DOMAINS = {
    "openrouter.ai",
    "huggingface.co",
    "github.com",
    "models.dev",
    "replicate.com",
    "together.ai",
    "fireworks.ai",
    "groq.com",
    "deepinfra.com",
    "ollama.com",
    "lmstudio.ai",
}


# Domains that are obvious placeholders and must never be published
# as official websites.
PLACEHOLDER_DOMAINS = {
    "example.com",
    "example.org",
    "example.net",
}


def normalize_text(value: object) -> str:
    """Normalize whitespace while preserving meaningful text."""
    if pd.isna(value):
        return ""

    text = str(value).strip()
    text = re.sub(r"\s+", " ", text)

    return text


def normalize_name(value: object) -> str:
    """Create a normalized identity used for duplicate detection."""
    text = normalize_text(value).lower()

    text = text.replace("–", "-")
    text = text.replace("—", "-")

    text = re.sub(r"[^a-z0-9]+", " ", text)

    return re.sub(r"\s+", " ", text).strip()


def clean_url(value: object) -> str:
    """Basic URL normalization."""
    value = normalize_text(value)

    if not value:
        return ""

    return value.rstrip("/")


def get_domain(url: object) -> str:
    """Return a normalized hostname from a URL."""
    value = normalize_text(url)

    if not value:
        return ""

    try:
        parsed = urlparse(value)

        hostname = parsed.hostname or ""
        hostname = hostname.lower()

        if hostname.startswith("www."):
            hostname = hostname[4:]

        return hostname

    except Exception:
        return ""


def is_third_party_url(url: object) -> bool:
    """Check whether a URL belongs to a known discovery/provider platform."""
    domain = get_domain(url)

    if not domain:
        return False

    if domain in THIRD_PARTY_DOMAINS:
        return True

    return any(
        domain.endswith("." + item)
        for item in THIRD_PARTY_DOMAINS
    )


def is_placeholder_url(url: object) -> bool:
    """Check whether a URL belongs to an obvious placeholder domain."""
    domain = get_domain(url)

    if not domain:
        return False

    if domain in PLACEHOLDER_DOMAINS:
        return True

    return any(
        domain.endswith("." + item)
        for item in PLACEHOLDER_DOMAINS
    )


def website_status(row: pd.Series) -> str:
    """Classify the provenance of the supplied website."""
    website = normalize_text(row.get("official_website", ""))

    if not website:
        return "missing"

    if is_placeholder_url(website):
        return "placeholder"

    if is_third_party_url(website):
        return "third_party_reference"

    return "candidate_official"


def make_model_id(row: pd.Series) -> str:
    """Generate a deterministic internal model ID."""
    company = normalize_name(row.get("company", ""))
    model = normalize_name(row.get("model_name", ""))

    identity = f"{company}-{model}"

    identity = re.sub(
        r"[^a-z0-9]+",
        "-",
        identity,
    ).strip("-")

    return f"model-{identity}"


def clean_dataset() -> None:
    print("=" * 70)
    print("AI Orbit - Bulk Model Cleaning")
    print("=" * 70)

    # ------------------------------------------------------------
    # 1. Validate input
    # ------------------------------------------------------------

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}"
        )

    print(f"\nInput: {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE)

    original_rows = len(df)

    print(f"Original rows: {original_rows}")
    print(f"Original columns: {len(df.columns)}")

    # ------------------------------------------------------------
    # 2. Normalize text fields
    # ------------------------------------------------------------

    text_columns = [
        "model_name",
        "model_family",
        "company",
        "official_website",
        "official_model_page",
        "model_type",
        "primary_task",
        "description",
        "reasoning",
        "function_calling",
        "structured_output",
        "vision",
        "audio",
        "multimodal",
        "api_available",
        "open_weight",
        "license",
        "huggingface_url",
        "github_url",
        "official_docs",
        "pricing_model",
        "model_page_slug_check",
        "source",
        "official_logo_url",
    ]

    for column in text_columns:
        if column in df.columns:
            df[column] = df[column].map(normalize_text)

    # ------------------------------------------------------------
    # 3. Normalize URL fields
    # ------------------------------------------------------------

    url_columns = [
        "official_website",
        "official_model_page",
        "huggingface_url",
        "github_url",
        "official_docs",
        "official_logo_url",
    ]

    for column in url_columns:
        if column in df.columns:
            df[column] = df[column].map(clean_url)

    # ------------------------------------------------------------
    # 4. Remove records without model names
    # ------------------------------------------------------------

    before_name_filter = len(df)

    df = df[
        df["model_name"].str.len() > 0
    ].copy()

    missing_name_removed = (
        before_name_filter - len(df)
    )

    # ------------------------------------------------------------
    # 5. Create normalized model identity
    # ------------------------------------------------------------

    df["_normalized_model_name"] = (
        df["model_name"].map(normalize_name)
    )

    # ------------------------------------------------------------
    # 6. Remove duplicate model records
    # ------------------------------------------------------------

    before_dedup = len(df)

    if "quality_score" in df.columns:
        df["quality_score"] = pd.to_numeric(
            df["quality_score"],
            errors="coerce",
        )

        # Prefer higher quality records when duplicate
        # model names exist.
        df = df.sort_values(
            by=[
                "_normalized_model_name",
                "quality_score",
            ],
            ascending=[
                True,
                False,
            ],
            na_position="last",
        )

    df = df.drop_duplicates(
        subset=["_normalized_model_name"],
        keep="first",
    ).copy()

    duplicates_removed = (
        before_dedup - len(df)
    )

    # ------------------------------------------------------------
    # 7. Analyze website provenance
    # ------------------------------------------------------------

    df["website_domain"] = (
        df["official_website"].map(get_domain)
    )

    df["website_is_third_party"] = (
        df["official_website"].map(is_third_party_url)
    )

    df["website_is_placeholder"] = (
        df["official_website"].map(is_placeholder_url)
    )

    df["website_provenance"] = df.apply(
        website_status,
        axis=1,
    )

    # ------------------------------------------------------------
    # 8. Analyze model-page provenance
    # ------------------------------------------------------------

    df["model_page_domain"] = (
        df["official_model_page"].map(get_domain)
    )

    df["model_page_is_third_party"] = (
        df["official_model_page"].map(
            is_third_party_url
        )
    )

    # ------------------------------------------------------------
    # 9. Preserve supplied URLs as reference information
    # ------------------------------------------------------------

    df["source_reference_url"] = (
        df["official_model_page"]
    )

    # Keep the supplied website as a candidate until verified.
    df["official_website_candidate"] = (
        df["official_website"]
    )

    # Remove obviously unsafe values from the candidate
    # official website field.
    invalid_website_mask = (
        df["website_is_third_party"]
        | df["website_is_placeholder"]
    )

    df.loc[
        invalid_website_mask,
        "official_website_candidate",
    ] = ""

    # ------------------------------------------------------------
    # 10. Discovery source
    # ------------------------------------------------------------

    df["discovery_source"] = df["source"]

    # ------------------------------------------------------------
    # 11. Generate deterministic internal IDs
    # ------------------------------------------------------------

    df["id"] = df.apply(
        make_model_id,
        axis=1,
    )

    # ------------------------------------------------------------
    # 12. Reorder important columns
    # ------------------------------------------------------------

    priority_columns = [
        "id",
        "model_name",
        "model_family",
        "company",
        "description",
        "model_type",
        "primary_task",
        "official_website_candidate",
        "official_model_page",
        "source_reference_url",
        "website_provenance",
        "official_logo_url",
        "license",
        "context_window",
        "max_output",
        "reasoning",
        "function_calling",
        "structured_output",
        "vision",
        "audio",
        "multimodal",
        "api_available",
        "open_weight",
        "pricing_model",
        "input_cost_per_mtok",
        "output_cost_per_mtok",
        "huggingface_url",
        "github_url",
        "official_docs",
        "discovery_source",
        "quality_score",
        "website_domain",
        "website_is_third_party",
        "website_is_placeholder",
        "model_page_domain",
        "model_page_is_third_party",
    ]

    existing_priority = [
        column
        for column in priority_columns
        if column in df.columns
    ]

    remaining_columns = [
        column
        for column in df.columns
        if column not in existing_priority
        and not column.startswith("_")
    ]

    df = df[
        existing_priority + remaining_columns
    ]

    # ------------------------------------------------------------
    # 13. Final cleanup
    # ------------------------------------------------------------

    df = df.replace("", pd.NA)

    df = df.sort_values(
        by=[
            "company",
            "model_name",
        ],
        na_position="last",
    ).reset_index(drop=True)

    # ------------------------------------------------------------
    # 14. Save cleaned dataset
    # ------------------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    # ------------------------------------------------------------
    # 15. Calculate report metrics
    # ------------------------------------------------------------

    candidate_official_count = int(
        (
            df["website_provenance"]
            == "candidate_official"
        ).sum()
    )

    third_party_count = int(
        (
            df["website_provenance"]
            == "third_party_reference"
        ).sum()
    )

    placeholder_count = int(
        (
            df["website_provenance"]
            == "placeholder"
        ).sum()
    )

    missing_website_count = int(
        (
            df["website_provenance"]
            == "missing"
        ).sum()
    )

    unique_companies = (
        df["company"]
        .dropna()
        .nunique()
    )

    # ------------------------------------------------------------
    # 16. Generate cleaning report
    # ------------------------------------------------------------

    report_lines = [
        "AI Orbit - Bulk Model Cleaning Report",
        "=" * 50,
        "",
        f"Input rows: {original_rows}",
        f"Output rows: {len(df)}",
        f"Columns: {len(df.columns)}",
        f"Rows removed for missing model name: "
        f"{missing_name_removed}",
        f"Duplicate model identities removed: "
        f"{duplicates_removed}",
        "",
        f"Unique companies/providers: "
        f"{unique_companies}",
        "",
        "Website provenance:",
        f"  Candidate official: "
        f"{candidate_official_count}",
        f"  Third-party reference: "
        f"{third_party_count}",
        f"  Placeholder: "
        f"{placeholder_count}",
        f"  Missing: "
        f"{missing_website_count}",
        "",
        "Data-quality policy:",
        "Third-party discovery/provider URLs are preserved",
        "as source_reference_url.",
        "They are NOT treated as official websites.",
        "Placeholder domains such as example.com are removed",
        "from official_website_candidate.",
        "",
    ]

    REPORT_FILE.write_text(
        "\n".join(report_lines),
        encoding="utf-8",
    )

    # ------------------------------------------------------------
    # 17. Console summary
    # ------------------------------------------------------------

    print("\nCleaning complete.")
    print("-" * 70)

    print(
        f"Input rows:                 {original_rows}"
    )

    print(
        f"Output rows:                {len(df)}"
    )

    print(
        f"Duplicates removed:         "
        f"{duplicates_removed}"
    )

    print(
        f"Missing names removed:      "
        f"{missing_name_removed}"
    )

    print(
        f"Unique companies/providers: "
        f"{unique_companies}"
    )

    print()
    print("Website provenance:")

    print(
        f"  Candidate official:       "
        f"{candidate_official_count}"
    )

    print(
        f"  Third-party reference:    "
        f"{third_party_count}"
    )

    print(
        f"  Placeholder:              "
        f"{placeholder_count}"
    )

    print(
        f"  Missing:                  "
        f"{missing_website_count}"
    )

    print()
    print(
        f"Cleaned CSV: {OUTPUT_FILE}"
    )

    print(
        f"Report:      {REPORT_FILE}"
    )

    print("=" * 70)


if __name__ == "__main__":
    clean_dataset()