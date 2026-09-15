from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]
INPUT_PATH = BASE_DIR / "data" / "processed" / "bulk_models_cleaned.csv"
OUTPUT_PATH = BASE_DIR / "data" / "processed" / "bulk_models_with_domains.csv"


KNOWN_PROVIDER_DOMAINS = {
    "anthropic": "https://www.anthropic.com",
    "openai": "https://openai.com",
    "google": "https://google.com",
    "google-deepmind": "https://deepmind.google",
    "meta": "https://meta.com",
    "microsoft": "https://microsoft.com",
    "amazon": "https://aws.amazon.com",
    "aws": "https://aws.amazon.com",
    "cohere": "https://cohere.com",
    "mistral": "https://mistral.ai",
    "mistralai": "https://mistral.ai",
    "deepseek": "https://www.deepseek.com",
    "minimax": "https://www.minimaxi.com",
    "moonshot-ai": "https://www.moonshot.cn",
    "moonshotai": "https://www.moonshot.cn",
    "nvidia": "https://www.nvidia.com",
    "ibm": "https://www.ibm.com",
    "ibm-granite": "https://www.ibm.com",
    "perplexity": "https://www.perplexity.ai",
    "runway": "https://runway.com",
    "snowflake": "https://www.snowflake.com",
    "stability-ai": "https://stability.ai",
    "thinking-machines": "https://thinkingmachines.ai",
    "alibaba": "https://www.alibaba.com",

    "qwen": "https://qwen.ai",
    "zhipu-ai": "https://www.zhipuai.cn",
    "z-ai": "https://www.zhipuai.cn",
    "xiaomi": "https://www.mi.com",
    "nousresearch": "https://nousresearch.com",
    "aion-labs": "https://www.aionlabs.ai",
    "sakana-ai": "https://sakana.ai",
    "kwaipilot": "https://kwaipilot.ai",
    "sarvam-ai": "https://www.sarvam.ai",
    "reka-ai": "https://reka.ai",
    "relace": "https://relace.ai",
    "inception": "https://www.inceptionlabs.ai",

    "bytedance-seed": "https://seed.bytedance.com",
    "xai": "https://x.ai",
    "tencent": "https://www.tencent.com",
    "poolside": "https://www.poolside.ai",
    "arcee-ai": "https://www.arcee.ai",
    "upstage": "https://www.upstage.ai",
    "jina-ai": "https://jina.ai",

    "assemblyai": "https://www.assemblyai.com",
    "baai": "https://www.baai.ac.cn",
    "bytedance": "https://seed.bytedance.com",
    "deepgram": "https://deepgram.com",
    "ideogram": "https://ideogram.ai",
    "inclusionai": "https://www.inclusion-ai.org",
    "luma-ai": "https://luma.ai",
    "nomic-ai": "https://www.nomic.ai",
    "playht": "https://playht.co",
    "rekaai": "https://reka.ai",
    "swiss-ai": "https://www.swiss-ai.org",
    "voyage-ai": "https://www.voyageai.com",
}


PROVIDER_ALIASES = {
    "anthropic": "anthropic",
    "openai": "openai",
    "google": "google",
    "google-deepmind": "google-deepmind",
    "deepmind": "google-deepmind",

    "qwen": "qwen",
    "qwenlm": "qwen",

    "z-ai": "z-ai",
    "z.ai": "z-ai",
    "zhipu": "zhipu-ai",
    "zhipu ai": "zhipu-ai",
    "zhipuai": "zhipu-ai",

    "bytedance": "bytedance",
    "bytedance-seed": "bytedance-seed",
    "bytedance seed": "bytedance-seed",
    "seed": "bytedance-seed",

    "xai": "xai",
    "x-ai": "x-ai",
    "x.ai": "xai",

    "tencent": "tencent",
    "poolside": "poolside",
    "arcee": "arcee-ai",
    "arcee ai": "arcee-ai",
    "arcee-ai": "arcee-ai",
    "upstage": "upstage",
    "jina": "jina-ai",
    "jina ai": "jina-ai",
    "jina-ai": "jina-ai",

    "assemblyai": "assemblyai",
    "assembly ai": "assemblyai",
    "baai": "baai",
    "beijing academy of artificial intelligence": "baai",
    "deepgram": "deepgram",
    "ideogram": "ideogram",
    "inclusionai": "inclusionai",
    "inclusion ai": "inclusionai",
    "luma-ai": "luma-ai",
    "luma ai": "luma-ai",
    "nomic-ai": "nomic-ai",
    "nomic ai": "nomic-ai",
    "playht": "playht",
    "playht ai": "playht",
    "rekaai": "rekaai",
    "reka ai": "reka-ai",
    "swiss-ai": "swiss-ai",
    "swiss ai": "swiss-ai",
    "voyage-ai": "voyage-ai",
    "voyage ai": "voyage-ai",

    "google": "google",
    "meta": "meta",
    "microsoft": "microsoft",
    "amazon": "amazon",
    "aws": "aws",
    "cohere": "cohere",
    "mistral": "mistral",
    "mistralai": "mistralai",
    "deepseek": "deepseek",
    "minimax": "minimax",
    "moonshot-ai": "moonshot-ai",
    "moonshotai": "moonshotai",
    "nvidia": "nvidia",
    "ibm": "ibm",
    "ibm-granite": "ibm-granite",
    "perplexity": "perplexity",
    "runway": "runway",
    "snowflake": "snowflake",
    "stability-ai": "stability-ai",
    "thinking-machines": "thinking-machines",
    "alibaba": "alibaba",

    "dots studio": "dots-studio",
    "dots-studio": "dots-studio",

    "nex agi": "nex-agi",
    "nex-agi": "nex-agi",

    "openrouter": "openrouter",
    "models.dev": "models-dev",
    "models-dev": "models-dev",

    "hugging face": "hugging-face",
    "hugging-face": "hugging-face",
}


UNSAFE_PROVIDERS = {
    "openrouter",
    "models-dev",
    "modelsdev",
}


PLACEHOLDER_DOMAINS = {
    "example.com",
    "example.org",
    "example.net",
}


COMMUNITY_PROVIDERS = {
    "huggingface",
    "hugging-face",
    "openrouter",
    "models.dev",
    "models-dev",
    "github",
}


def normalize_provider(value: object) -> str:
    if value is None:
        return ""

    value = str(value).strip().lower()

    if value.startswith("~"):
        value = value[1:]

    return " ".join(value.replace("_", " ").split())


def canonicalize_provider(value: object) -> str:
    normalized = normalize_provider(value)

    if not normalized:
        return ""

    return PROVIDER_ALIASES.get(
        normalized,
        normalized.replace(" ", "-"),
    )


def normalize_domain(value: object) -> str:
    if value is None:
        return ""

    value = str(value).strip()

    if not value:
        return ""

    if "://" not in value:
        value = "https://" + value

    try:
        parsed = urlparse(value)
        domain = parsed.netloc.lower().split(":")[0]

        if domain.startswith("www."):
            domain = domain[4:]

        return domain.rstrip(".")
    except Exception:
        return ""


def is_placeholder_domain(value: object) -> bool:
    domain = normalize_domain(value)
    return domain in PLACEHOLDER_DOMAINS


def is_third_party_reference_url(value: object) -> bool:
    domain = normalize_domain(value)

    if not domain:
        return False

    if domain in COMMUNITY_PROVIDERS:
        return True

    if domain.endswith(".github.io"):
        return True

    if domain.endswith(".github.com"):
        return True

    if domain == "github.com" or domain.endswith(".github.com"):
        return True

    if domain == "huggingface.co" or domain.endswith(".huggingface.co"):
        return True

    if domain == "openrouter.ai" or domain.endswith(".openrouter.ai"):
        return True

    if domain == "models.dev" or domain.endswith(".models.dev"):
        return True

    return False


def provider_domain_matches(
    provider: object,
    domain: object,
) -> bool:
    provider = canonicalize_provider(provider)
    domain = normalize_domain(domain)

    if not provider or not domain:
        return False

    expected = KNOWN_PROVIDER_DOMAINS.get(provider)

    if not expected:
        return False

    expected_domain = normalize_domain(expected)

    return (
        domain == expected_domain
        or domain.endswith("." + expected_domain)
    )


def resolve_provider_domain(
    provider: object,
) -> tuple[str, str | None, str]:
    canonical = canonicalize_provider(provider)

    if not canonical:
        return "", None, "unresolved"

    if canonical in UNSAFE_PROVIDERS:
        return canonical, None, "unsafe_mapping"

    domain = KNOWN_PROVIDER_DOMAINS.get(canonical)

    if domain:
        return canonical, domain, "resolved"

    return canonical, None, "unresolved"


def choose_official_website(
    candidate: object,
    provider_domain: str | None,
) -> tuple[str | None, str]:
    if provider_domain:
        return provider_domain, "provider_registry"

    if candidate is None:
        return None, "none"

    candidate = str(candidate).strip()

    if not candidate:
        return None, "none"

    if is_placeholder_domain(candidate):
        return None, "rejected_placeholder"

    if is_third_party_reference_url(candidate):
        return None, "rejected_third_party"

    return candidate, "candidate_unverified"


def main() -> None:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_PATH}"
        )

    df = pd.read_csv(INPUT_PATH)

    print(f"Input rows: {len(df)}")

    provider_results = df["company"].apply(resolve_provider_domain)

    df["provider_canonical"] = provider_results.apply(
        lambda x: x[0]
    )

    df["provider_official_domain"] = provider_results.apply(
        lambda x: x[1]
    )

    df["provider_resolution_status"] = provider_results.apply(
        lambda x: x[2]
    )

    if "official_website" not in df.columns:
        df["official_website"] = pd.NA

    website_results = df.apply(
        lambda row: choose_official_website(
            row.get("official_website"),
            row["provider_official_domain"],
        ),
        axis=1,
    )

    df["official_website"] = website_results.apply(
        lambda x: x[0]
    )

    df["website_provenance"] = website_results.apply(
        lambda x: x[1]
    )

    # Strict rule:
    # provider resolution does NOT equal website verification.
    # bulk_website.py must perform the HTTP verification gate.
    unresolved_mask = df["provider_resolution_status"].isin(
        ["unresolved", "unsafe_mapping"]
    )

    df.loc[unresolved_mask, "official_website"] = pd.NA

    df.loc[
        unresolved_mask,
        "website_provenance",
    ] = df.loc[
        unresolved_mask,
        "website_provenance",
    ].replace(
        "candidate_unverified",
        "candidate_unverified",
    )

    df["verification_notes"] = ""

    df.loc[
        df["provider_resolution_status"] == "resolved",
        "verification_notes",
    ] = (
        "Provider domain resolved through controlled registry; "
        "HTTP verification required before publication."
    )

    df.loc[
        df["provider_resolution_status"] == "unresolved",
        "verification_notes",
    ] = (
        "No official provider domain was available for "
        "automatic verification."
    )

    df.loc[
        df["provider_resolution_status"] == "unsafe_mapping",
        "verification_notes",
    ] = (
        "Provider mapping intentionally blocked because the "
        "available reference is third-party or unsafe."
    )

    df.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print("\nProvider resolution status:")
    print(
        df["provider_resolution_status"]
        .value_counts()
        .to_string()
    )

    print(
        f"\nOutput written to: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()