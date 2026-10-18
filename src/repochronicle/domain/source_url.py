"""Safe source URL validation; credentials must never be embedded in a URL."""

from urllib.parse import urlparse


class InvalidSourceURL(ValueError):
    """Raised when a source URL is outside the configured policy."""


def validate_repository_url(
    url: str,
    allowed_hosts: set[str],
    *,
    allow_insecure_http: bool = False,
) -> str:
    """Validate and canonicalize a repository URL against an explicit host allowlist.

    HTTPS is required unless the caller deliberately enables HTTP for a trusted private
    installation. Non-default ports are preserved because self-managed Git hosts use them.
    """
    try:
        parsed = urlparse(url.strip())
        port = parsed.port
    except ValueError as exc:
        raise InvalidSourceURL("Repository URL is malformed") from exc

    if parsed.scheme != "https" and not (allow_insecure_http and parsed.scheme == "http"):
        raise InvalidSourceURL("HTTPS is required unless insecure HTTP is explicitly enabled")
    if parsed.username or parsed.password:
        raise InvalidSourceURL("Credentials must not be embedded in a repository URL")
    if not parsed.hostname:
        raise InvalidSourceURL("Repository URL must include a hostname")

    host = parsed.hostname.lower().rstrip(".")
    normalized_allowed = {item.lower().rstrip(".") for item in allowed_hosts if item.strip()}
    if host not in normalized_allowed:
        raise InvalidSourceURL(f"Repository host '{host}' is not in the configured allowlist")
    if parsed.query or parsed.fragment:
        raise InvalidSourceURL("Repository URLs must not contain query strings or fragments")

    path = parsed.path.rstrip("/")
    if not path or path == "/":
        raise InvalidSourceURL("Repository URL must identify a repository path")

    authority = f"{host}:{port}" if port is not None else host
    return f"{parsed.scheme}://{authority}{path}"
