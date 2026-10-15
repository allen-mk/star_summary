"""渲染：Markdown + JSON 输出，统计基于统一数据形状。"""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .models import ClassifiedRepo
from .taxonomy import Taxonomy

_TEMPLATE_DIR = Path(__file__).parent / "templates"


def compute_stats(items: List[ClassifiedRepo]) -> Dict[str, Any]:
    language_counter = Counter()
    category_counter = Counter()
    total_stars = 0

    for item in items:
        repo = item.repo
        total_stars += repo.stargazers_count
        if repo.language:
            language_counter[repo.language] += 1
        for cat in item.classification.categories:
            category_counter[cat] += 1

    return {
        "total_repos": len(items),
        "total_stars": total_stars,
        "language_stats": dict(language_counter.most_common(10)),
        "category_stats": dict(category_counter.most_common(15)),
        "category_count": len(category_counter),
    }


def _group_by_category(items: List[ClassifiedRepo]) -> Dict[str, List[ClassifiedRepo]]:
    grouped: Dict[str, List[ClassifiedRepo]] = {}
    for item in items:
        for cat in item.classification.categories:
            grouped.setdefault(cat, []).append(item)
    # 组内按星标排序，组按数量排序
    for cat_items in grouped.values():
        cat_items.sort(key=lambda i: i.repo.stargazers_count, reverse=True)
    return dict(sorted(grouped.items(), key=lambda kv: len(kv[1]), reverse=True))


def _env(template_dir: Path) -> Environment:
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=select_autoescape(disabled_extensions=("md",), default=False),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    def format_number(value):
        try:
            return f"{int(value):,}"
        except (TypeError, ValueError):
            return str(value)

    def format_date(value, fmt="%Y-%m-%d"):
        if not value:
            return ""
        if isinstance(value, datetime):
            return value.strftime(fmt)
        text = str(value)
        try:
            dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
            return dt.strftime(fmt)
        except ValueError:
            return text

    env.filters["format_number"] = format_number
    env.filters["format_date"] = format_date
    return env


def render_markdown(
    items: List[ClassifiedRepo],
    taxonomy: Taxonomy,
    template_dir: Path = _TEMPLATE_DIR,
) -> str:
    env = _env(template_dir)
    template = env.get_template("main.md")
    grouped = _group_by_category(items)
    stats = compute_stats(items)
    return template.render(
        items=items,
        grouped=grouped,
        stats=stats,
        taxonomy=taxonomy,
        generated_at=datetime.now(timezone.utc).astimezone(),
    )


def render_json(items: List[ClassifiedRepo], taxonomy: Taxonomy) -> str:
    stats = compute_stats(items)
    payload = {
        "metadata": {
            "version": "2.0.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_repos": stats["total_repos"],
            "total_categories": stats["category_count"],
        },
        "statistics": {
            "by_language": stats["language_stats"],
            "by_category": stats["category_stats"],
            "total_stars": stats["total_stars"],
        },
        "repositories": [item.to_dict() for item in items],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)
