from __future__ import annotations


# Known relationships where the product/tool name
# differs from the company's official domain.
#
# This is verification metadata, not discovery data.
KNOWN_PROVIDER_DOMAINS: dict[str, set[str]] = {
    "claude": {
        "anthropic.com",
    },
    "chatgpt": {
        "openai.com",
        "chatgpt.com",
    },
    "junie by jetbrains": {
        "jetbrains.com",
        "junie.jetbrains.com",
    },
        "mejorar - ai photo enhancer": {"mejorarcalidaddeimagen.ai"},
}


def provider_domain_matches(
    entity_name: str,
    url: str,
) -> bool:
    """
    Check whether a URL belongs to a known provider domain
    for an entity.
    """

    from urllib.parse import urlparse

    domain = (urlparse(url).hostname or "").lower()

    if domain.startswith("www."):
        domain = domain[4:]

    normalized_name = entity_name.strip().lower()

    allowed_domains = KNOWN_PROVIDER_DOMAINS.get(
        normalized_name,
        set(),
    )

    return any(
        domain == allowed
        or domain.endswith(f".{allowed}")
        for allowed in allowed_domains
    )