"""规则分类：语言 + 关键词/topics 匹配，多标签输出。"""

from __future__ import annotations

from typing import List

from .models import Classification, ClassifiedRepo, Repo
from .taxonomy import Taxonomy


def _search_text(repo: Repo) -> str:
    # full_name 里的 '-' 也视作分隔，让 model-context-protocol 能命中 model-context-protocol / mcp 之外的写法
    parts = [repo.name, repo.description or "", repo.full_name.replace("/", " ").replace("-", " ")]
    return " ".join(p for p in parts if p).lower()


def classify_repo(repo: Repo, taxonomy: Taxonomy) -> ClassifiedRepo:
    categories: List[str] = []

    lang_cat = taxonomy.language_category(repo.language)
    categories.append(lang_cat)

    text = _search_text(repo)
    topics = {t.lower() for t in repo.topics}
    # 连字符/下划线归一，让 model-context-protocol 能命中 mcp、model context protocol 等写法
    text_norm = text.replace("-", " ").replace("_", " ")
    text_compact = text_norm.replace(" ", "")

    for category_id, keywords in taxonomy.keyword_categories().items():
        for kw in keywords:
            kw = kw.lower()
            kw_norm = kw.replace("-", " ").replace("_", " ")
            if (
                kw in text
                or kw_norm in text_norm
                or kw_norm.replace(" ", "") in text_compact
                or kw in topics
            ):
                categories.append(category_id)
                break

    # 去重并保持顺序
    seen = set()
    ordered = []
    for c in categories:
        if c not in seen and taxonomy.is_valid(c):
            seen.add(c)
            ordered.append(c)

    if not ordered:
        ordered = ["uncategorized"]

    confidence = 0.8 if len(ordered) > 1 or ordered != ["uncategorized"] else 0.3
    classification = Classification(
        categories=ordered,
        method="rules",
        confidence=confidence,
        reasoning=f"语言 {repo.language or '未知'} + 关键词/topics 匹配",
    )
    return repo.with_classification(classification)


def classify_batch(repos, taxonomy: Taxonomy) -> List[ClassifiedRepo]:
    return [classify_repo(r, taxonomy) for r in repos]
