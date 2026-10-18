import json

from repochronicle.cli import main


def test_doctor_reports_foundation_phase(capsys) -> None:
    assert main(["doctor"]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["phase"] == "F0"


def test_repository_url_cli_rejects_embedded_credentials(capsys) -> None:
    assert main(["validate-repository-url", "https://user:secret@github.com/acme/repo"]) == 2
    rendered = capsys.readouterr().out
    output = json.loads(rendered)
    assert output["valid"] is False
    assert "secret" not in rendered
