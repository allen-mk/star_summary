import json
from pathlib import Path

from star_summary.classify import classify_repo
from star_summary.models import Repo
from star_summary.taxonomy import Taxonomy

FIXTURE = Path(__file__).parent / "fixtures" / "starred_sample.json"


def load_by_name(name):
    repos = json.loads(FIXTURE.read_text(encoding="utf-8"))
    return next(r for r in repos if r["full_name"] == name)


def make_repo(name):
    return Repo.from_dict(load_by_name(name))


def test_language_category_always_present():
    tax = Taxonomy.load_default()
    repo = make_repo("microsoft/vscode")
    result = classify_repo(repo, tax)
    assert "lang-typescript" in result.classification.categories


def test_topics_drive_tech_category():
    tax = Taxonomy.load_default()
    repo = make_repo("modelcontextprotocol/servers")
    result = classify_repo(repo, tax)
    assert "mcp" in result.classification.categories


def test_llm_keywords_match():
    tax = Taxonomy.load_default()
    repo = make_repo("langchain-ai/langchain")
    result = classify_repo(repo, tax)
    assert "agent" in result.classification.categories or "llm" in result.classification.categories


def test_unknown_repo_falls_back_to_language_only():
    tax = Taxonomy.load_default()
    repo = Repo(
        name="nothing",
        full_name="nobody/nothing",
        description="",
        html_url="https://github.com/nobody/nothing",
        language="Cobol",
        topics=[],
        stargazers_count=1,
        forks_count=0,
        updated_at="2026-01-01T00:00:00+00:00",
    )
    result = classify_repo(repo, tax)
    assert result.classification.categories == ["lang-other"]
    assert result.classification.method == "rules"


def test_no_invalid_categories_leak():
    tax = Taxonomy.load_default()
    for raw in json.loads(FIXTURE.read_text(encoding="utf-8")):
        result = classify_repo(Repo.from_dict(raw), tax)
        for cat in result.classification.categories:
            assert tax.is_valid(cat), f"invalid category {cat} for {raw['full_name']}"
