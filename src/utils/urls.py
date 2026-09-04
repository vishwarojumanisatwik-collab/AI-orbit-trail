from urllib.parse import urlparse, urlunparse


TRACKING_PARAMETERS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "fbclid",
    "gclid",
}


def normalize_url(url: str) -> str:
    """
    Normalize a URL for comparison.
    This does not prove that the URL is official.
    It only creates a consistent representation.
    """
    parsed = urlparse(url.strip())

    scheme = parsed.scheme.lower() or "https"

    hostname = (parsed.hostname or "").lower()

    if hostname.startswith("www."):
        hostname = hostname[4:]

    path = parsed.path.rstrip("/")

    if not path:
        path = ""

    return urlunparse(
        (scheme, hostname, path, "", "", "")
    )


def get_domain(url: str) -> str:
    """Return the normalized hostname."""
    parsed = urlparse(url.strip())

    hostname = (parsed.hostname or "").lower()

    if hostname.startswith("www."):
        hostname = hostname[4:]

    return hostname