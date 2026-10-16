"""渲染：Markdown + JSON 输出，统计基于统一数据形状。"""

from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .brief import Brief
from .models import ClassifiedRepo

_TEMPLATE_DIR = Path(__file__).parent / "templates"
_SLUG_PUNCT = re.compile(
    r"[\]\[!\"#$%&'()*+,./:;<=>?@\\^_`{|}~。，、；：？！…—·「」『』（）【】《》〈〉“”‘’]"
)


def github_slug(heading: str) -> str:
    """与 GitHub、Cursor 预览一致：小写，空格变连字符。"""
    text = _SLUG_PUNCT.sub("", str(heading).strip().lower())
    text = re.sub(r"\s+", "-", text)
    return text.strip("-")


def compute_stats(items: List[ClassifiedRepo]) -> Dict[str, Any]:
    language_counter = Counter()
    category_counter = Counter()
    total_stars = 0

    for item in items:
        repo = item.repo
        total_stars += repo.stargazers_count
        if repo.language:
            language_counter[repo.language] += 1
        category_counter[item.classification.category] += 1

    return {
        "total_repos": len(items),
        "total_stars": total_stars,
        "language_stats": dict(language_counter.most_common(10)),
        "category_stats": dict(category_counter.most_common(15)),
        "category_count": len(category_counter),
    }


def _group_by_category(items: List[ClassifiedRepo], brief: Brief) -> Dict[str, List[ClassifiedRepo]]:
    grouped: Dict[str, List[ClassifiedRepo]] = {name: [] for name in brief.names()}
    for item in items:
        grouped.setdefault(item.classification.category, []).append(item)
    for cat_items in grouped.values():
        cat_items.sort(key=lambda i: i.repo.stargazers_count, reverse=True)
    ordered = [(name, grouped[name]) for name in brief.names() if grouped.get(name)]
    extra = [name for name in grouped if name not in brief.names() and grouped[name]]
    ordered.extend((name, grouped[name]) for name in extra)
    return dict(ordered)


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
    env.filters["github_slug"] = github_slug
    return env


def render_markdown(
    items: List[ClassifiedRepo],
    brief: Brief,
    template_dir: Path = _TEMPLATE_DIR,
) -> str:
    env = _env(template_dir)
    template = env.get_template("main.md")
    grouped = _group_by_category(items, brief)
    stats = compute_stats(items)
    return template.render(
        items=items,
        grouped=grouped,
        stats=stats,
        generated_at=datetime.now(timezone.utc).astimezone(),
    )


def render_json(items: List[ClassifiedRepo]) -> str:
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
