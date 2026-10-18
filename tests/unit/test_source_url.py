import pytest

from repochronicle.domain.source_url import InvalidSourceURL, validate_repository_url

ALLOWED = {"github.com", "gitlab.com", "gitlab.internal.example"}


def test_normalizes_allowed_repository_url() -> None:
    assert validate_repository_url(
        "https://GitHub.com/Example/Project.git/",
        ALLOWED,
    ) == "https://github.com/Example/Project.git"


@pytest.mark.parametrize(
    "url",
    [
        "file:///etc/passwd",
        "http://github.com/acme/private",
        "https://[invalid/acme/repo",
        "https://user:secret@github.com/acme/private",
        "https://evil.example/acme/repo",
        "https://github.com/",
        "https://github.com/acme/repo?token=secret",
        "https://github.com/acme/repo#branch",
    ],
)
def test_rejects_unsafe_repository_urls(url: str) -> None:
    with pytest.raises(InvalidSourceURL):
        validate_repository_url(url, ALLOWED)


def test_allows_explicitly_configured_self_managed_gitlab() -> None:
    result = validate_repository_url(
        "https://gitlab.internal.example/platform/api",
        ALLOWED,
    )
    assert result == "https://gitlab.internal.example/platform/api"


def test_preserves_explicit_port_for_self_managed_git_host() -> None:
    assert validate_repository_url(
        "https://gitlab.internal.example:8443/platform/api",
        ALLOWED,
    ) == "https://gitlab.internal.example:8443/platform/api"


def test_http_requires_explicit_opt_in_for_private_installations() -> None:
    assert validate_repository_url(
        "http://gitlab.internal.example/platform/api",
        ALLOWED,
        allow_insecure_http=True,
    ) == "http://gitlab.internal.example/platform/api"
