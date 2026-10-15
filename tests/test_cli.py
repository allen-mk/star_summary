import json
from pathlib import Path

from click.testing import CliRunner

from star_summary.cli import cli

FIXTURE = Path(__file__).parent / "fixtures" / "starred_sample.json"


class FakeClient:
    def __init__(self):
        self._repos = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def fetch_all(self):
        return self._repos

    def validate(self):
        return {"login": "fake", "core_remaining": 4999, "core_limit": 5000}


def test_generate_markdown(tmp_path, monkeypatch):
    monkeypatch.setattr("star_summary.cli.GitHubClient", lambda **kw: FakeClient())
    monkeypatch.setenv("GITHUB_TOKEN", "fake")
    runner = CliRunner()
    result = runner.invoke(cli, ["generate", "--output", str(tmp_path), "--no-cache"])
    assert result.exit_code == 0, result.output
    md = tmp_path / "README.md"
    assert md.exists()
    content = md.read_text(encoding="utf-8")
    assert "microsoft/vscode" in content
    assert "项目总数" in content


def test_generate_json(tmp_path, monkeypatch):
    monkeypatch.setattr("star_summary.cli.GitHubClient", lambda **kw: FakeClient())
    monkeypatch.setenv("GITHUB_TOKEN", "fake")
    runner = CliRunner()
    result = runner.invoke(cli, ["generate", "--output", str(tmp_path), "--format", "json", "--no-cache"])
    assert result.exit_code == 0, result.output
    data = json.loads((tmp_path / "starred_repos.json").read_text(encoding="utf-8"))
    assert data["metadata"]["total_repos"] > 0
    assert data["repositories"][0]["classification"]["categories"]


def test_generate_both(tmp_path, monkeypatch):
    monkeypatch.setattr("star_summary.cli.GitHubClient", lambda **kw: FakeClient())
    monkeypatch.setenv("GITHUB_TOKEN", "fake")
    runner = CliRunner()
    result = runner.invoke(cli, ["generate", "--output", str(tmp_path), "--format", "both", "--no-cache"])
    assert result.exit_code == 0, result.output
    assert (tmp_path / "README.md").exists()
    assert (tmp_path / "starred_repos.json").exists()


def test_generate_requires_token(tmp_path, monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    runner = CliRunner()
    result = runner.invoke(cli, ["generate", "--output", str(tmp_path), "--no-cache"])
    assert result.exit_code != 0
    assert "GITHUB_TOKEN" in result.output


def test_validate(monkeypatch):
    monkeypatch.setattr("star_summary.cli.GitHubClient", lambda **kw: FakeClient())
    monkeypatch.setenv("GITHUB_TOKEN", "fake")
    runner = CliRunner()
    result = runner.invoke(cli, ["validate"])
    assert result.exit_code == 0, result.output
    assert "fake" in result.output
