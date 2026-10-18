import tomllib
from pathlib import Path


def test_canonical_migration_is_included_in_the_installed_package() -> None:
    root = Path(__file__).resolve().parents[2]
    with (root / "pyproject.toml").open("rb") as stream:
        project = tomllib.load(stream)

    mapping = project["tool"]["hatch"]["build"]["targets"]["wheel"]["force-include"]
    assert mapping["migrations/001_foundation.sql"] == (
        "repochronicle/migrations/sql/001_foundation.sql"
    )
    assert (root / "migrations" / "001_foundation.sql").is_file()
