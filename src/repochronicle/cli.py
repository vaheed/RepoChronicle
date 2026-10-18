"""Small administrative CLI for the foundation scaffold."""

import argparse
import json
from collections.abc import Sequence

from repochronicle import __version__
from repochronicle.config import get_settings
from repochronicle.domain.source_url import InvalidSourceURL, validate_repository_url


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="repochronicle")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("doctor", help="validate basic local configuration")
    subparsers.add_parser("status", help="print current scaffold and feature status")
    validate_parser = subparsers.add_parser(
        "validate-repository-url",
        help=(
            "validate a URL against the configured Git host allowlist "
            "without contacting the provider"
        ),
    )
    validate_parser.add_argument("url")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    settings = get_settings()
    if args.command == "doctor":
        result = {
            "name": "RepoChronicle",
            "version": __version__,
            "phase": "F0",
            "database_url_configured": bool(settings.database_url),
            "valkey_url_configured": bool(settings.valkey_url),
            "llm_configured": bool(settings.llm_base_url and settings.llm_model),
            "embedding_provider": settings.embedding_provider,
            "warning": (
                "doctor does not test network connectivity; "
                "use /health/ready after Compose startup"
            ),
        }
        print(json.dumps(result, indent=2))
        return 0
    if args.command == "status":
        print(
            json.dumps(
                {"name": "RepoChronicle", "version": __version__, "phase": "F0"},
                indent=2,
            )
        )
        return 0
    if args.command == "validate-repository-url":
        allowed_hosts = {host.strip() for host in settings.allowed_git_hosts.split(",")}
        try:
            normalized = validate_repository_url(args.url, allowed_hosts)
        except InvalidSourceURL as exc:
            print(json.dumps({"valid": False, "reason": str(exc)}, indent=2))
            return 2
        print(json.dumps({"valid": True, "canonical_url": normalized}, indent=2))
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
