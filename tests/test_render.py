import json
from pathlib import Path

from star_summary.classify import classify_batch
from star_summary.models import Repo
from star_summary.render import render_markdown, render_json, compute_stats
from star_summary.taxonomy import Taxonomy

FIXTURE = Path(__file__).parent / "fixtures" / "starred_sample.json"


def classified():
    tax = Taxonomy.load_default()
    repos = [Repo.from_dict(r) for r in json.loads(FIXTURE.read_text(encoding="utf-8"))]
    return classify_batch(repos, tax)


def test_stats_not_zero():
    items = classified()
    stats = compute_stats(items)
    assert stats["total_repos"] == len(items)
    assert stats["total_stars"] > 0
    assert stats["language_stats"], "语言统计不应为空"
    assert stats["category_stats"], "分类统计不应为空"


def test_render_markdown_contains_sections():
    items = classified()
    md = render_markdown(items, Taxonomy.load_default())
    assert "项目总数" in md
    assert "microsoft/vscode" in md
    assert "统计信息" in md


def test_render_json_shape():
    items = classified()
    data = json.loads(render_json(items, Taxonomy.load_default()))
    assert data["metadata"]["total_repos"] == len(items)
    assert data["repositories"]
    first = data["repositories"][0]
    assert "classification" in first
    assert "categories" in first["classification"]
