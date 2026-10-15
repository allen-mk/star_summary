"""词表回归：锁定典型仓库的分类结果，防止合并词表时漂移。"""

import json
from pathlib import Path

from star_summary.classify import classify_repo
from star_summary.models import Repo
from star_summary.taxonomy import Taxonomy

FIXTURE = Path(__file__).parent / "fixtures" / "starred_sample.json"

TAX = Taxonomy.load_default()


def classify(name):
    repos = json.loads(FIXTURE.read_text(encoding="utf-8"))
    raw = next(r for r in repos if r["full_name"] == name)
    return classify_repo(Repo.from_dict(raw), TAX).classification.categories


def test_vscode_is_typescript_desktop():
    cats = classify("microsoft/vscode")
    assert "lang-typescript" in cats
    assert "desktop" in cats


def test_langchain_is_llm_agent():
    cats = classify("langchain-ai/langchain")
    assert "lang-python" in cats
    assert "llm" in cats or "agent" in cats


def test_mcp_servers_is_mcp():
    cats = classify("modelcontextprotocol/servers")
    assert "mcp" in cats


def test_free_programming_books_is_learning():
    cats = classify("EbookFoundation/free-programming-books")
    assert "learning" in cats or "awesome-list" in cats


def test_transformers_is_ai_ml():
    cats = classify("huggingface/transformers")
    assert "ai-ml" in cats
    assert "llm" in cats


def test_crawlee_is_browser_automation():
    cats = classify("apify/crawlee")
    assert "browser-automation" in cats
