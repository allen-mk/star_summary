import json
from pathlib import Path

from star_summary.brief import default_brief
from star_summary.models import Classification, Repo
from star_summary.render import compute_stats, render_json, render_markdown

FIXTURE = Path(__file__).parent / "fixtures" / "starred_sample.json"


def classified():
    repos = [Repo.from_dict(item) for item in json.loads(FIXTURE.read_text(encoding="utf-8"))]
    return [repo.with_classification(Classification(category="编程工具")) for repo in repos]


def test_stats_not_zero():
    items = classified()
    stats = compute_stats(items)
    assert stats["total_repos"] == len(items)
    assert stats["total_stars"] > 0
    assert stats["language_stats"]
    assert stats["category_stats"] == {"编程工具": len(items)}


def test_toc_anchor_matches_preview_slug():
    from star_summary.brief import Brief, CategorySpec

    repo = Repo(name="demo", full_name="o/demo", html_url="https://github.com/o/demo")
    items = [repo.with_classification(Classification(category="Agent-Skills"))]
    brief = Brief([CategorySpec("Agent-Skills", "")], "", "")
    md = render_markdown(items, brief)
    assert "](#agent-skills)" in md
    assert "](#Agent-Skills)" not in md


def test_render_markdown_contains_sections():
    items = classified()
    md = render_markdown(items, default_brief())
    assert "项目总数" in md
    assert md.count("microsoft/vscode") == 1
    assert "编程工具" in md


def test_render_json_shape():
    items = classified()
    data = json.loads(render_json(items))
    assert data["metadata"]["total_repos"] == len(items)
    first = data["repositories"][0]
    assert first["category"] == "编程工具"
    assert "full_name" in first
    assert "html_url" in first
