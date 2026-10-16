"""分类说明：类别、偏好、硬性规则。"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

import yaml

UNCLASSIFIED = "未归类"

_DEFAULT_CATEGORIES = [
    ("人工智能", "模型、智能体、机器学习和提示词相关的星标。按它是干什么的判断，不按实现语言。"),
    ("编程工具", "编辑器、构建、调试、命令行，以及日常写代码会用到的工具。"),
    ("Web 开发", "浏览器里的应用、前后端框架、网站和 HTTP 接口。"),
    ("客户端与界面", "桌面应用、移动应用和界面组件。"),
    ("系统与基础设施", "操作系统、运行时、容器、部署和云。"),
    ("数据与存储", "数据库、数据管道和分析。"),
    ("安全", "认证、加密、漏洞和安全工具。"),
    ("学习与资料", "教程、书籍、手册和资料合集。"),
    (UNCLASSIFIED, "没有更合适的类别时放这里。"),
]


@dataclass
class CategorySpec:
    name: str
    description: str


@dataclass
class Brief:
    categories: List[CategorySpec]
    preferences: str
    hard_rules: str

    def names(self) -> List[str]:
        return [category.name for category in self.categories]


def default_brief() -> Brief:
    return Brief(
        categories=[CategorySpec(name, description) for name, description in _DEFAULT_CATEGORIES],
        preferences="",
        hard_rules="",
    )


def load_brief(path) -> Brief:
    """读取分类说明。文件不存在时使用默认类别，偏好和硬性规则为空。"""
    brief_path = Path(path)
    if not brief_path.exists():
        return default_brief()
    data = yaml.safe_load(brief_path.read_text(encoding="utf-8")) or {}
    raw_categories = data.get("categories")
    if not raw_categories:
        categories = list(default_brief().categories)
    else:
        categories = [
            CategorySpec(str(item["name"]), str(item.get("description") or ""))
            for item in raw_categories
        ]
        if UNCLASSIFIED not in {category.name for category in categories}:
            categories.append(CategorySpec(UNCLASSIFIED, "没有更合适的类别时放这里。"))
    return Brief(
        categories=categories,
        preferences=str(data.get("preferences") or ""),
        hard_rules=str(data.get("hard_rules") or ""),
    )


def resolve_category(name: str, brief: Brief) -> str:
    if name in brief.names():
        return name
    return UNCLASSIFIED
