from __future__ import annotations

from collections import Counter
from pathlib import Path
import re

import pandas as pd


INPUT_PATH = Path("data/processed/bulk_models_cleaned.csv")
OUTPUT_PATH = Path("data/processed/bulk_models_with_domains.csv")
REPORT_PATH = Path("data/processed/bulk_provider_domain_report.txt")


# Canonical provider -> official first-party domain.
# Only providers with sufficiently reliable identity evidence are mapped.
KNOWN_PROVIDER_DOMAINS = {
    # Major providers
    "openai": "https://openai.com",
    "anthropic": "https://www.anthropic.com",
    "google": "https://google.com",
    "google-deepmind": "https://deepmind.google",
    "deepmind": "https://deepmind.google",
    "microsoft": "https://microsoft.com",
    "meta": "https://meta.com",
    "mistralai": "https://mistral.ai",
    "mistral": "https://mistral.ai",
    "cohere": "https://cohere.com",
    "xai": "https://x.ai",
    "ai21": "https://ai21.com",
    "ai21-labs": "https://ai21.com",
    "amazon": "https://aws.amazon.com",
    "amazon-web-services": "https://aws.amazon.com",
    "aws": "https://aws.amazon.com",

    # Enterprise / established AI companies
    "ibm": "https://www.ibm.com",
    "ibm-granite": "https://www.ibm.com",
    "ibm granite": "https://www.ibm.com",
    "ibm_granite": "https://www.ibm.com",
    "ibm granite models": "https://www.ibm.com",

    "nvidia": "https://www.nvidia.com",
    "databricks": "https://www.databricks.com",
    "snowflake": "https://www.snowflake.com",
    "salesforce": "https://www.salesforce.com",
    "oracle": "https://www.oracle.com",
    "intel": "https://www.intel.com",
    "qualcomm": "https://www.qualcomm.com",
    "samsung": "https://www.samsung.com",

    # AI labs / research organizations
    "thinking-machines": "https://thinkingmachines.ai",
    "thinkingmachines": "https://thinkingmachines.ai",

    "01-ai": "https://01.ai",
    "01ai": "https://01.ai",

    "allenai": "https://allenai.org",
    "allen-institute-for-ai": "https://allenai.org",

    "stability-ai": "https://stability.ai",
    "stabilityai": "https://stability.ai",

    "black-forest-labs": "https://blackforestlabs.ai",
    "black-forest-labs-ai": "https://blackforestlabs.ai",

    "runway": "https://runway.com",
    "runwayml": "https://runway.com",

    "perplexity": "https://www.perplexity.ai",
    "perplexity-ai": "https://www.perplexity.ai",

    "character-ai": "https://character.ai",
    "characterai": "https://character.ai",

    "reka": "https://reka.ai",

    "writer": "https://writer.com",

    "inflection": "https://inflection.ai",

    "together-ai": "https://www.together.ai",
    "togetherai": "https://www.together.ai",

    "fireworks-ai": "https://fireworks.ai",
    "fireworksai": "https://fireworks.ai",

    "groq": "https://groq.com",

    "deepseek": "https://www.deepseek.com",
    "deepseek-ai": "https://www.deepseek.com",

    "qwen": "https://qwenlm.github.io",
    "qwenlm": "https://qwenlm.github.io",
    "alibaba": "https://www.alibaba.com",

    "moonshot-ai": "https://www.moonshot.cn",
    "moonshotai": "https://www.moonshot.cn",

    "zhipu-ai": "https://www.zhipuai.cn",
    "zhipu": "https://www.zhipuai.cn",

    "baichuan": "https://www.baichuan-ai.com",

    "minimax": "https://www.minimaxi.com",

    "01-ai": "https://01.ai",

    # Robotics / specialized organizations
    "figure": "https://www.figure.ai",
    "figure-ai": "https://www.figure.ai",

    "physical-intelligence": "https://www.physicalintelligence.company",

    "sanctuary-ai": "https://www.sanctuary.ai",

    # Community / project organizations where an official organization/project
    # can be identified reliably.
    "dots-studio": "https://huggingface.co/dots-llm",
    "dotsstudio": "https://huggingface.co/dots-llm",

    "mplug": "https://github.com/X-PLUG",
    "m-plug": "https://github.com/X-PLUG",

    "nex-agi": "https://github.com/nex-agi",
    "nexagi": "https://github.com/nex-agi",
}


# Provider aliases -> canonical provider name.
# This is intentionally conservative.
PROVIDER_ALIASES = {
    # OpenAI
    "open ai": "openai",
    "open_ai": "openai",

    # Anthropic
    "anthropic-ai": "anthropic",

    # Google
    "google-ai": "google",
    "google ai": "google",
    "google deepmind": "google-deepmind",
    "google-deepmind": "google-deepmind",

    # Meta
    "meta-ai": "meta",
    "meta ai": "meta",

    # Mistral
    "mistral-ai": "mistralai",
    "mistral ai": "mistralai",

    # IBM Granite
    "ibm-granite": "ibm",
    "ibm granite": "ibm",
    "ibm_granite": "ibm",
    "ibm granite models": "ibm",

    # Stability AI
    "stability ai": "stability-ai",

    # Black Forest Labs
    "black forest labs": "black-forest-labs",

    # Runway
    "runway ml": "runway",
    "runwayml": "runway",

    # Together
    "together ai": "together-ai",
    "togetherai": "together-ai",

    # Fireworks
    "fireworks ai": "fireworks-ai",
    "fireworksai": "fireworks-ai",

    # Thinking Machines
    "thinking machines": "thinking-machines",
    "thinkingmachines": "thinkingmachines",
    "thinking-machines": "thinking-machines",

    # Dots Studio
    "dots studio": "dots-studio",
    "dots-studio": "dots-studio",

    # mPLUG
    "m plug": "mplug",
    "m-plug": "mplug",
    "mplug": "mplug",

    # Nex AGI
    "nex agi": "nex-agi",
    "nex-agi": "nex-agi",

    # OpenRouter is a discovery / routing platform.
    "open router": "openrouter",
    "openrouter": "openrouter",
}


# These identities must NOT be treated as official model-provider domains.
# They are routing/discovery platforms rather than first-party providers.
UNSAFE_PROVIDERS = {
    "openrouter",
    "models-dev",
    "modelsdev",
}


# Placeholder domains from the supplied dataset.
PLACEHOLDER_DOMAINS = {
    "example.com",
    "example.org",
    "example.net",
}


# Community/model accounts for which we intentionally avoid guessing
# a corporate website.
COMMUNITY_PROVIDERS = {
    "alpha-vllm",
    "anthracite-org",
    "cognitivecomputations",
    "gryphe",
    "mancer",
    "perceptron",
    "sao10k",
    "thedrummer",
    "undi95",
    "hugging-face",
}


def normalize_provider(value: object) -> str:
    """Normalize a provider/company name into a comparison key."""
    if value is None or pd.isna(value):
        return ""

    text = str(value).strip().lower()

    text = text.replace("&", " and ")
    text = text.replace("/", " ")
    text = text.replace("\\", " ")

    text = re.sub(r"[^a-z0-9]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text.replace(" ", "-")


def canonicalize_provider(provider: object) -> str:
    """Resolve aliases to a canonical provider identifier."""
    normalized = normalize_provider(provider)

    if not normalized:
        return ""

    # Direct alias lookup first.
    if normalized in PROVIDER_ALIASES:
        return PROVIDER_ALIASES[normalized]

    # Direct known-provider match.
    if normalized in KNOWN_PROVIDER_DOMAINS:
        return normalized

    # Community providers are deliberately retained as unresolved identities.
    if normalized in COMMUNITY_PROVIDERS:
        return normalized

    return normalized


def clean_url(value: object) -> str:
    """Return a normalized URL or an empty string."""
    if value is None or pd.isna(value):
        return ""

    value = str(value).strip()

    if not value:
        return ""

    if not re.match(r"^https?://", value, flags=re.I):
        value = "https://" + value

    return value.rstrip("/")


def domain_from_url(url: object) -> str:
    """Extract a basic hostname from a URL."""
    url = clean_url(url)

    if not url:
        return ""

    match = re.match(r"^https?://([^/]+)", url, flags=re.I)

    if not match:
        return ""

    return match.group(1).lower().split(":")[0]


def is_placeholder_url(url: object) -> bool:
    domain = domain_from_url(url)

    if not domain:
        return False

    return domain in PLACEHOLDER_DOMAINS


def is_openrouter_url(url: object) -> bool:
    domain = domain_from_url(url)

    return (
        domain == "openrouter.ai"
        or domain.endswith(".openrouter.ai")
    )


def is_third_party_reference_url(url: object) -> bool:
    domain = domain_from_url(url)

    if not domain:
        return False

    return (
        domain == "openrouter.ai"
        or domain.endswith(".openrouter.ai")
        or domain == "huggingface.co"
        or domain.endswith(".huggingface.co")
        or domain == "github.com"
        or domain.endswith(".github.com")
        or domain == "models.dev"
        or domain.endswith(".models.dev")
    )


def resolve_provider_domain(provider: object) -> tuple[str, str, str]:
    """
    Return:
        canonical_provider,
        official_domain,
        resolution_status
    """
    canonical = canonicalize_provider(provider)

    if not canonical:
        return "", "", "missing_provider"

    if canonical in UNSAFE_PROVIDERS:
        return canonical, "", "unsafe_mapping"

    if canonical in KNOWN_PROVIDER_DOMAINS:
        return (
            canonical,
            KNOWN_PROVIDER_DOMAINS[canonical],
            "resolved",
        )

    return canonical, "", "unresolved"


def choose_official_website(
    candidate_url: object,
    provider_official_domain: object,
) -> tuple[str, str]:
    """
    Return the official website and provenance.

    The supplied dataset's website is treated as a candidate/reference,
    never as automatically trusted.
    """
    provider_domain = clean_url(provider_official_domain)
    candidate = clean_url(candidate_url)

    if provider_domain:
        return provider_domain, "provider_registry"

    if candidate and not is_placeholder_url(candidate):
        if not is_third_party_reference_url(candidate):
            return candidate, "candidate_unverified"

    return "", "unresolved"


def main() -> None:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_PATH}"
        )

    df = pd.read_csv(INPUT_PATH)

    if "company" not in df.columns:
        raise ValueError(
            "Expected 'company' column was not found."
        )

    records = []

    for _, row in df.iterrows():
        record = row.to_dict()

        company = row.get("company", "")
        candidate_url = row.get("official_website_candidate", "")
        model_page = row.get("official_model_page", "")
        source_reference = row.get("source_reference_url", "")

        (
            canonical_provider,
            provider_domain,
            resolution_status,
        ) = resolve_provider_domain(company)

        official_website, website_provenance = choose_official_website(
            candidate_url,
            provider_domain,
        )

        model_page = clean_url(model_page)
        source_reference = clean_url(source_reference)

        record["website_domain"] = domain_from_url(official_website)

        record["website_is_third_party"] = (
            is_third_party_reference_url(official_website)
        )

        record["website_is_placeholder"] = (
            is_placeholder_url(official_website)
        )

        record["model_page_domain"] = domain_from_url(model_page)

        record["model_page_is_third_party"] = (
            is_third_party_reference_url(model_page)
        )

        record["official_website"] = official_website

        record["provider_canonical"] = canonical_provider
        record["provider_official_domain"] = provider_domain
        record["provider_resolution_status"] = resolution_status

        # Keep source provenance explicit.
        record["website_provenance"] = website_provenance

        records.append(record)

    output_df = pd.DataFrame(records)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    output_df.to_csv(OUTPUT_PATH, index=False)

    total_rows = len(output_df)

    status_counts = Counter(
        output_df["provider_resolution_status"].fillna("")
    )

    resolved_records = status_counts.get("resolved", 0)
    unresolved_records = status_counts.get("unresolved", 0)
    unsafe_records = status_counts.get("unsafe_mapping", 0)
    missing_records = status_counts.get("missing_provider", 0)

    provider_count = (
        output_df["provider_canonical"]
        .replace("", pd.NA)
        .dropna()
        .nunique()
    )

    unresolved_providers = (
        output_df.loc[
            output_df["provider_resolution_status"] == "unresolved",
            "provider_canonical",
        ]
        .value_counts()
        .sort_index()
    )

    unsafe_providers = (
        output_df.loc[
            output_df["provider_resolution_status"] == "unsafe_mapping",
            "provider_canonical",
        ]
        .value_counts()
        .sort_index()
    )

    resolution_rate = (
        resolved_records / total_rows * 100
        if total_rows
        else 0
    )

    report_lines = [
        "AI ORBIT - BULK PROVIDER DOMAIN RESOLUTION",
        "=" * 60,
        "",
        f"Original rows: {total_rows}",
        f"Input rows: {total_rows}",
        f"Original providers: {df['company'].nunique(dropna=True)}",
        f"Canonical providers: {provider_count}",
        "",
        f"Resolved records: {resolved_records}",
        f"Unresolved records: {unresolved_records}",
        f"Unsafe mappings: {unsafe_records}",
        f"Missing providers: {missing_records}",
        "",
        f"Resolution rate: {resolution_rate:.2f}%",
        "",
        f"Unresolved providers: {len(unresolved_providers)}",
        "",
        "UNRESOLVED PROVIDERS",
        "-" * 60,
    ]

    if unresolved_providers.empty:
        report_lines.append("None")
    else:
        for provider, count in unresolved_providers.items():
            report_lines.append(
                f"{provider}: {count} record(s)"
            )

    report_lines.extend(
        [
            "",
            f"Unsafe provider identities: {len(unsafe_providers)}",
            "",
            "UNSAFE / BLOCKED PROVIDERS",
            "-" * 60,
        ]
    )

    if unsafe_providers.empty:
        report_lines.append("None")
    else:
        for provider, count in unsafe_providers.items():
            report_lines.append(
                f"{provider}: {count} record(s)"
            )

    report_lines.extend(
        [
            "",
            "DATA QUALITY POLICY",
            "-" * 60,
            "Unverified providers are left unresolved rather than being assigned speculative official domains.",
            "OpenRouter, Models.dev and Hugging Face are treated as discovery/reference platforms, not first-party model-provider websites.",
            "Community/model accounts are intentionally unresolved when a reliable official organization cannot be established.",
        ]
    )

    REPORT_PATH.write_text(
        "\n".join(report_lines),
        encoding="utf-8",
    )

    print("Provider domain resolution complete.")
    print()
    print(f"Input rows: {total_rows}")
    print(f"Input providers: {df['company'].nunique(dropna=True)}")
    print(f"Canonical providers: {provider_count}")
    print()
    print(f"Resolved records: {resolved_records}")
    print(f"Unresolved records: {unresolved_records}")
    print(f"Unsafe mappings: {unsafe_records}")
    print(f"Missing providers: {missing_records}")
    print()
    print(f"Resolution rate: {resolution_rate:.2f}%")
    print()
    print(f"Output: {OUTPUT_PATH.resolve()}")
    print(f"Report: {REPORT_PATH.resolve()}")


if __name__ == "__main__":
    main()