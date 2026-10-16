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


def _set_model_env(monkeypatch, api_key="fake-key"):
    monkeypatch.setenv("STAR_SUMMARY_BASE_URL", "https://example.test/v1")
    monkeypatch.setenv("STAR_SUMMARY_MODEL", "fake")
    if api_key is None:
        monkeypatch.delenv("STAR_SUMMARY_API_KEY", raising=False)
    else:
        monkeypatch.setenv("STAR_SUMMARY_API_KEY", api_key)


def _invoke_generate(tmp_path, monkeypatch, extra_args):
    monkeypatch.setenv("GITHUB_TOKEN", "fake")
    _set_model_env(monkeypatch)
    monkeypatch.setattr("star_summary.cli.GitHubClient", lambda **kw: FakeClient())
    monkeypatch.setattr("star_summary.cli.ModelClient", FakeModel)
    runner = CliRunner()
    args = ["generate", "--config", str(_model_config(tmp_path)), "--output", str(tmp_path / "out"), "--no-cache"]
    args.extend(extra_args)
    return runner.invoke(cli, args)


def test_generate_markdown(tmp_path, monkeypatch):
    result = _invoke_generate(tmp_path, monkeypatch, ["--format", "markdown"])
    assert result.exit_code == 0, result.output
    content = (tmp_path / "out" / "README.md").read_text(encoding="utf-8")
    assert content.count("microsoft/vscode") == 1
    assert "项目总数" in content


def test_generate_json(tmp_path, monkeypatch):
    result = _invoke_generate(tmp_path, monkeypatch, ["--format", "json"])
    assert result.exit_code == 0, result.output
    data = json.loads((tmp_path / "out" / "starred_repos.json").read_text(encoding="utf-8"))
    assert data["metadata"]["total_repos"] > 0
    assert data["repositories"][0]["category"] == "编程工具"


def _generate(tmp_path, monkeypatch, config_text):
    monkeypatch.setenv("GITHUB_TOKEN", "fake")
    _set_model_env(monkeypatch)
    monkeypatch.setattr("star_summary.cli.GitHubClient", lambda **kw: FakeClient())
    monkeypatch.setattr("star_summary.cli.ModelClient", FakeModel)
    cfg = tmp_path / "config.yaml"
    cfg.write_text(config_text, encoding="utf-8")
    runner = CliRunner()
    return runner.invoke(
        cli,
        ["generate", "--config", str(cfg), "--output", str(tmp_path / "out"), "--no-cache"],
    )


def test_format_markdown_skips_json_file(tmp_path, monkeypatch):
    result = _generate(tmp_path, monkeypatch, "output:\n  format: markdown\n")
    assert result.exit_code == 0, result.output
    assert (tmp_path / "out" / "README.md").exists()
    assert not (tmp_path / "out" / "starred_repos.json").exists()


def test_format_both_writes_json_file(tmp_path, monkeypatch):
    result = _generate(tmp_path, monkeypatch, "output:\n  format: both\n")
    assert result.exit_code == 0, result.output
    assert (tmp_path / "out" / "README.md").exists()
    assert (tmp_path / "out" / "starred_repos.json").exists()


def test_generate_both(tmp_path, monkeypatch):
    result = _invoke_generate(tmp_path, monkeypatch, ["--format", "both"])
    assert result.exit_code == 0, result.output
    assert (tmp_path / "out" / "README.md").exists()
    assert (tmp_path / "out" / "starred_repos.json").exists()


class FakeModel:
    def __init__(self, base_url, api_key, model, timeout=60):
        self.base_url = base_url
        self.api_key = api_key
        self.model = model

    def assign(self, brief, repos, description_language=""):
        return {repo.full_name: "编程工具" for repo in repos}


def _model_config(tmp_path):
    cfg = tmp_path / "config.yaml"
    cfg.write_text("output:\n  format: both\n", encoding="utf-8")
    return cfg


def test_generate_assigns_one_category(tmp_path, monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "fake")
    _set_model_env(monkeypatch)
    monkeypatch.setattr("star_summary.cli.GitHubClient", lambda **kw: FakeClient())
    monkeypatch.setattr("star_summary.cli.ModelClient", FakeModel)
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "generate",
            "--config",
            str(_model_config(tmp_path)),
            "--output",
            str(tmp_path / "out"),
            "--no-cache",
        ],
    )
    assert result.exit_code == 0, result.output
    content = (tmp_path / "out" / "README.md").read_text(encoding="utf-8")
    assert content.count("microsoft/vscode") == 1
    assert "编程工具" in content
    data = json.loads((tmp_path / "out" / "starred_repos.json").read_text(encoding="utf-8"))
    categories = [item["category"] for item in data["repositories"]]
    assert categories
    assert set(categories) == {"编程工具"}


class UnknownModel(FakeModel):
    def assign(self, brief, repos, description_language=""):
        return {repo.full_name: "根本不存在" for repo in repos}


class BrokenModel(FakeModel):
    def assign(self, brief, repos, description_language=""):
        from star_summary.model import ModelError

        raise ModelError("模型没有返回可解析的归属")


def test_unknown_category_becomes_uncategorized(tmp_path, monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "fake")
    _set_model_env(monkeypatch)
    monkeypatch.setattr("star_summary.cli.GitHubClient", lambda **kw: FakeClient())
    monkeypatch.setattr("star_summary.cli.ModelClient", UnknownModel)
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["generate", "--config", str(_model_config(tmp_path)), "--output", str(tmp_path / "out"), "--no-cache"],
    )
    assert result.exit_code == 0, result.output
    content = (tmp_path / "out" / "README.md").read_text(encoding="utf-8")
    assert "根本不存在" not in content
    assert "未归类" in content
    data = json.loads((tmp_path / "out" / "starred_repos.json").read_text(encoding="utf-8"))
    assert {item["category"] for item in data["repositories"]} == {"未归类"}


def test_unparseable_model_keeps_existing_output(tmp_path, monkeypatch):
    out = tmp_path / "out"
    out.mkdir()
    (out / "README.md").write_text("保留目录", encoding="utf-8")
    (out / "starred_repos.json").write_text("保留数据", encoding="utf-8")
    monkeypatch.setenv("GITHUB_TOKEN", "fake")
    _set_model_env(monkeypatch)
    monkeypatch.setattr("star_summary.cli.GitHubClient", lambda **kw: FakeClient())
    monkeypatch.setattr("star_summary.cli.ModelClient", BrokenModel)
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["generate", "--config", str(_model_config(tmp_path)), "--output", str(out), "--format", "both", "--no-cache"],
    )
    assert result.exit_code != 0
    assert (out / "README.md").read_text(encoding="utf-8") == "保留目录"
    assert (out / "starred_repos.json").read_text(encoding="utf-8") == "保留数据"


class SummaryModel(FakeModel):
    def assign(self, brief, repos, description_language=""):
        assert description_language == "zh-cn"
        from star_summary.models import Assignment

        return {
            repo.full_name: Assignment(category="编程工具", summary="微软出的代码编辑器")
            for repo in repos
        }


def test_description_language_rewrites_blurb(tmp_path, monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "fake")
    _set_model_env(monkeypatch)
    monkeypatch.setattr("star_summary.cli.GitHubClient", lambda **kw: FakeClient())
    monkeypatch.setattr("star_summary.cli.ModelClient", SummaryModel)
    cfg = tmp_path / "config.yaml"
    cfg.write_text(
        "output:\n  format: both\n  description_language: zh-CN\n",
        encoding="utf-8",
    )
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["generate", "--config", str(cfg), "--output", str(tmp_path / "out"), "--no-cache"],
    )
    assert result.exit_code == 0, result.output
    content = (tmp_path / "out" / "README.md").read_text(encoding="utf-8")
    assert "微软出的代码编辑器" in content
    assert "Visual Studio Code" not in content
    data = json.loads((tmp_path / "out" / "starred_repos.json").read_text(encoding="utf-8"))
    vscode = next(item for item in data["repositories"] if item["full_name"] == "microsoft/vscode")
    assert vscode["description"] == "Visual Studio Code"
    assert vscode["summary"] == "微软出的代码编辑器"


def test_generate_requires_model(tmp_path, monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "fake")
    monkeypatch.delenv("STAR_SUMMARY_API_KEY", raising=False)
    cfg = tmp_path / "config.yaml"
    cfg.write_text("output:\n  format: both\n", encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["generate", "--config", str(cfg), "--output", str(tmp_path / "out"), "--no-cache"],
    )
    assert result.exit_code != 0
    assert "模型" in result.output


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
