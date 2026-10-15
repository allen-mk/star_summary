"""分类词表加载与查询。

词表数据在 taxonomy.yaml，是唯一事实来源；本模块只读。
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import yaml

_DEFAULT_PATH = Path(__file__).parent / "taxonomy.yaml"


@dataclass
class Category:
    id: str
    name: str
    group: str
    keywords: List[str]


class Taxonomy:
    def __init__(self, data: dict):
        self._raw = data
        self._categories: Dict[str, Category] = {}
        for cid, spec in (data.get("categories") or {}).items():
            self._categories[cid] = Category(
                id=cid,
                name=spec.get("name", cid),
                group=spec.get("group", "tech_stack"),
                keywords=list(spec.get("keywords") or []),
            )
        self._language_mappings: Dict[str, str] = dict(data.get("language_mappings") or {})
        self._special: Dict[str, str] = dict(data.get("special") or {})

    @classmethod
    def load_default(cls) -> "Taxonomy":
        return cls.from_path(_DEFAULT_PATH)

    @classmethod
    def from_path(cls, path) -> "Taxonomy":
        with open(path, "r", encoding="utf-8") as f:
            return cls(yaml.safe_load(f))

    def is_valid(self, category_id: str) -> bool:
        return category_id in self._categories or category_id in self._special

    def display_name(self, category_id: str) -> str:
        if category_id in self._categories:
            return self._categories[category_id].name
        return self._special.get(category_id, category_id)

    def group_of(self, category_id: str) -> Optional[str]:
        cat = self._categories.get(category_id)
        return cat.group if cat else None

    def keywords_for(self, category_id: str) -> List[str]:
        cat = self._categories.get(category_id)
        return cat.keywords if cat else []

    def language_category(self, language: Optional[str]) -> str:
        if not language:
            return "lang-other"
        return self._language_mappings.get(language, "lang-other")

    def keyword_categories(self) -> Dict[str, List[str]]:
        return {cid: cat.keywords for cid, cat in self._categories.items() if cat.keywords}

    def all_category_ids(self) -> List[str]:
        return list(self._categories) + list(self._special)
