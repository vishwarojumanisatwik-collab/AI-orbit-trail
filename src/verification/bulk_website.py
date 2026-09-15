from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

import httpx
import pandas as pd

from src.config import REQUEST_TIMEOUT, USER_AGENT


# ============================================================================
# PATHS
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "bulk_models_with_domains.csv"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "bulk_models_website_verified.csv"
)

REPORT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "bulk_website_verification_report.txt"
)


# ============================================================================
# BLOCKED / THIRD-PARTY DOMAINS
# ============================================================================

BLOCKED_DOMAINS = {
    "openrouter.ai",
    "models.dev",
    "huggingface.co",
    "github.com",
    "example.com",
}


# ============================================================================
# HELPERS
# ============================================================================

def normalize_domain(value: object) -> str:
    """Normalize a URL/domain to a hostname."""

    if value is None:
        return ""

    text = str(value).strip()

    if not text or text.lower() in {
        "nan",
        "none",
        "null",
    }:
        return ""

    if "://" not in text:
        text = "https://" + text

    try:
        hostname = (
            urlparse(text)
            .hostname
            or ""
        ).lower().strip()

        if hostname.startswith("www."):
            hostname = hostname[4:]

        return hostname

    except Exception:
        return ""


def is_blocked_domain(value: object) -> bool:
    """Return True for known third-party/placeholder domains."""

    domain = normalize_domain(value)

    if not domain:
        return False

    if domain in BLOCKED_DOMAINS:
        return True

    return any(
        domain.endswith(f".{blocked}")
        for blocked in BLOCKED_DOMAINS
    )


def domains_match(
    expected_domain: str,
    actual_domain: str,
) -> bool:
    """
    Check whether two domains represent the same site family.

    Example:
        expected: anthropic.com
        actual: www.anthropic.com

    Subdomains are accepted because official websites may redirect
    to product/docs subdomains.
    """

    expected = normalize_domain(expected_domain)
    actual = normalize_domain(actual_domain)

    if not expected or not actual:
        return False

    return (
        actual == expected
        or actual.endswith(f".{expected}")
    )


# ============================================================================
# HTTP VERIFICATION
# ============================================================================

def verify_domain(
    expected_url: str,
) -> dict:
    """
    Verify one candidate official provider domain.

    This checks:
    1. URL is syntactically valid.
    2. Domain is not a blocked third-party domain.
    3. Website is reachable.
    4. Redirect destination remains within the expected domain family.
    """

    expected_domain = normalize_domain(expected_url)

    result = {
        "official_website": expected_url or "",
        "expected_domain": expected_domain,
        "final_url": "",
        "final_domain": "",
        "http_status": None,
        "reachable": False,
        "verification_status": "unverified",
        "verification_method": "",
        "verification_notes": "",
    }

    if not expected_domain:
        result["verification_status"] = "invalid_url"
        result["verification_notes"] = (
            "Official provider domain is missing or invalid."
        )
        return result

    if is_blocked_domain(expected_domain):
        result["verification_status"] = "blocked_domain"
        result["verification_method"] = "domain_policy"
        result["verification_notes"] = (
            "Domain is blocked because it is a known "
            "third-party, aggregation, or placeholder domain."
        )
        return result

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": (
            "text/html,application/xhtml+xml,"
            "application/xml;q=0.9,*/*;q=0.8"
        ),
    }

    try:
        with httpx.Client(
            timeout=REQUEST_TIMEOUT,
            follow_redirects=True,
            headers=headers,
        ) as client:

            response = client.get(expected_url)

            final_url = str(response.url)
            final_domain = normalize_domain(final_url)

            result["final_url"] = final_url
            result["final_domain"] = final_domain
            result["http_status"] = response.status_code

            # ----------------------------------------------------------------
            # Successful responses
            # ----------------------------------------------------------------

            if response.status_code == 200:

                if is_blocked_domain(final_domain):
                    result["verification_status"] = (
                        "failed_third_party_redirect"
                    )
                    result["verification_method"] = (
                        "http + redirect-domain-check"
                    )
                    result["verification_notes"] = (
                        "Website responded successfully but redirected "
                        "to a blocked third-party domain."
                    )
                    return result

                if domains_match(
                    expected_domain,
                    final_domain,
                ):
                    result["reachable"] = True
                    result["verification_status"] = "verified"
                    result["verification_method"] = (
                        "http + redirect-domain-check"
                    )
                    result["verification_notes"] = (
                        "Website returned HTTP 200 and the final "
                        "domain matches the expected provider domain."
                    )
                else:
                    result["reachable"] = True
                    result["verification_status"] = "manual_review"
                    result["verification_method"] = (
                        "http + redirect-domain-check"
                    )
                    result["verification_notes"] = (
                        "Website returned HTTP 200 but the final "
                        "domain differs from the expected provider domain."
                    )

                return result

            # ----------------------------------------------------------------
            # Access restricted
            # ----------------------------------------------------------------

            if response.status_code in {
                401,
                403,
                429,
            }:

                result["verification_status"] = "blocked"
                result["verification_method"] = "http"

                if domains_match(
                    expected_domain,
                    final_domain,
                ):
                    result["verification_notes"] = (
                        "The official domain responded but "
                        "automated access is restricted."
                    )
                else:
                    result["verification_notes"] = (
                        "Automated access is restricted and the "
                        "final domain differs from the expected domain."
                    )

                return result

            # ----------------------------------------------------------------
            # Other HTTP failures
            # ----------------------------------------------------------------

            result["verification_status"] = "failed"
            result["verification_method"] = "http"
            result["verification_notes"] = (
                f"Unexpected HTTP status {response.status_code}."
            )

            return result

    except httpx.TimeoutException:

        result["verification_status"] = "timeout"
        result["verification_method"] = "http"
        result["verification_notes"] = (
            f"Request timed out after {REQUEST_TIMEOUT} seconds."
        )

    except httpx.RequestError as exc:

        result["verification_status"] = "error"
        result["verification_method"] = "http"
        result["verification_notes"] = (
            f"HTTP request error: {exc}"
        )

    except Exception as exc:

        result["verification_status"] = "error"
        result["verification_method"] = "verification"
        result["verification_notes"] = (
            f"Unexpected verification error: {exc}"
        )

    return result


# ============================================================================
# MAIN PIPELINE
# ============================================================================

def main() -> None:

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_PATH}"
        )

    df = pd.read_csv(INPUT_PATH)

    required_columns = {
        "model_name",
        "company",
        "provider_canonical",
        "provider_official_domain",
        "provider_resolution_status",
    }

    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(sorted(missing))
        )

    verification_columns = [
        "official_website",
        "expected_domain",
        "final_url",
        "final_domain",
        "http_status",
        "reachable",
        "verification_status",
        "verification_method",
        "verification_notes",
    ]

    # Initialize columns.
    for column in verification_columns:
        df[column] = ""

    df["http_status"] = pd.NA
    df["reachable"] = False

    # Only HTTP-verify safely resolved provider domains.
    resolved_mask = (
        df["provider_resolution_status"]
        == "resolved"
    )

    resolved_indices = df.index[resolved_mask].tolist()

    print("Bulk website verification")
    print("=" * 60)
    print()
    print(f"Total records: {len(df)}")
    print(
        f"Resolved domains to verify: "
        f"{len(resolved_indices)}"
    )
    print(
        "Unresolved/unsafe records will remain "
        "unverified."
    )
    print()

    # ------------------------------------------------------------------------
    # Verify unique domains only.
    #
    # This is important because 585 records may represent far fewer
    # provider websites. We should not hit the same provider 20+ times.
    # ------------------------------------------------------------------------

    unique_domains = (
        df.loc[
            resolved_mask,
            "provider_official_domain",
        ]
        .dropna()
        .astype(str)
        .map(str.strip)
    )

    unique_domains = sorted(
        domain
        for domain in unique_domains.unique()
        if domain
    )

    print(
        f"Unique official domains to verify: "
        f"{len(unique_domains)}"
    )
    print()

    verification_cache: dict[str, dict] = {}

    for number, domain in enumerate(
        unique_domains,
        start=1,
    ):

        print(
            f"[{number}/{len(unique_domains)}] "
            f"Checking {domain}"
        )

        verification_cache[domain] = verify_domain(domain)

        status = verification_cache[domain][
            "verification_status"
        ]

        print(f"    -> {status}")

    # ------------------------------------------------------------------------
    # Apply cached verification results to records.
    # ------------------------------------------------------------------------

    for index in resolved_indices:

        domain = str(
            df.at[
                index,
                "provider_official_domain",
            ]
        ).strip()

        if not domain:
            continue

        verification = verification_cache.get(
            domain
        )

        if not verification:
            continue

        for column in verification_columns:

            df.at[
                index,
                column,
            ] = verification.get(
                column,
                "",
            )

    # ------------------------------------------------------------------------
    # Explicitly mark unresolved / unsafe records.
    # ------------------------------------------------------------------------

    unresolved_mask = (
        df["provider_resolution_status"]
        != "resolved"
    )

    df.loc[
        unresolved_mask,
        "verification_status",
    ] = "not_checked"

    df.loc[
        unresolved_mask,
        "verification_method",
    ] = "provider_resolution_policy"

    df.loc[
        unresolved_mask,
        "verification_notes",
    ] = (
        "No official provider domain was available for "
        "automatic verification."
    )

    # ------------------------------------------------------------------------
    # Do not expose an official website unless the provider mapping itself
    # was resolved and the verification stage produced an acceptable result.
    #
    # 'blocked' is retained separately because a 403/429 does not mean
    # the domain is fake; it only means automated access was restricted.
    # ------------------------------------------------------------------------

    acceptable_statuses = {
    "verified",
    }

    accepted_mask = (
        df["verification_status"]
        .isin(acceptable_statuses)
    )

    df["official_website"] = ""

    df.loc[
        accepted_mask,
        "official_website",
    ] = df.loc[
        accepted_mask,
        "provider_official_domain",
    ]

    # ------------------------------------------------------------------------
    # Save output.
    # ------------------------------------------------------------------------

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    # ------------------------------------------------------------------------
    # Build report.
    # ------------------------------------------------------------------------

    status_counts = (
        df["verification_status"]
        .value_counts()
        .to_dict()
    )

    verified = int(
        status_counts.get("verified", 0)
    )

    blocked = int(
        status_counts.get("blocked", 0)
    )

    failed = int(
        status_counts.get("failed", 0)
    )

    timeout = int(
        status_counts.get("timeout", 0)
    )

    errors = int(
        status_counts.get("error", 0)
    )

    manual_review = int(
        status_counts.get("manual_review", 0)
    )

    not_checked = int(
        status_counts.get("not_checked", 0)
    )

    invalid_url = int(
        status_counts.get("invalid_url", 0)
    )

    blocked_domain = int(
        status_counts.get("blocked_domain", 0)
    )

    failed_redirect = int(
        status_counts.get(
            "failed_third_party_redirect",
            0,
        )
    )

    report_lines = [
        "AI ORBIT - BULK WEBSITE VERIFICATION",
        "=" * 60,
        "",
        f"Total records: {len(df)}",
        f"Resolved provider records: {len(resolved_indices)}",
        f"Unique domains checked: {len(unique_domains)}",
        "",
        "VERIFICATION RESULTS",
        "-" * 60,
        f"Verified: {verified}",
        f"Blocked / access restricted: {blocked}",
        f"Manual review: {manual_review}",
        f"Failed: {failed}",
        f"Timeout: {timeout}",
        f"HTTP / request errors: {errors}",
        f"Invalid URL: {invalid_url}",
        f"Blocked third-party domain: {blocked_domain}",
        f"Third-party redirect: {failed_redirect}",
        f"Not checked: {not_checked}",
        "",
        "DATA QUALITY POLICY",
        "-" * 60,
        (
            "Only safely resolved provider domains were subjected "
            "to HTTP verification."
        ),
        (
            "Provider domains were verified once per unique domain "
            "and cached across model records."
        ),
        (
            "OpenRouter, Models.dev, Hugging Face and example.com "
            "remain blocked from official website output."
        ),
        (
            "HTTP 403/401/429 responses are classified as blocked "
            "rather than incorrectly treated as invalid websites."
        ),
        (
            "Redirects to a different domain are sent to manual review "
            "or rejected when they land on a known third-party domain."
        ),
        "",
        f"Output: {OUTPUT_PATH}",
        f"Report: {REPORT_PATH}",
    ]

    REPORT_PATH.write_text(
        "\n".join(report_lines),
        encoding="utf-8",
    )

    # ------------------------------------------------------------------------
    # Console summary.
    # ------------------------------------------------------------------------

    print()
    print("=" * 60)
    print("Verification complete.")
    print()
    print(f"Verified: {verified}")
    print(f"Blocked: {blocked}")
    print(f"Manual review: {manual_review}")
    print(f"Failed: {failed}")
    print(f"Timeout: {timeout}")
    print(f"Errors: {errors}")
    print(f"Not checked: {not_checked}")
    print()
    print(f"Output: {OUTPUT_PATH}")
    print(f"Report: {REPORT_PATH}")


if __name__ == "__main__":
    main()
