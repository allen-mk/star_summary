"""统一的数据形状：Repo + Classification。

旧代码里同一概念有三种结构（扁平 / {repo, classification} / 合并字段），
这里固定为一种：ClassifiedRepo = Repo + Classification，序列化时保持扁平。
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


@dataclass
class Repo:
    name: str
    full_name: str
    html_url: str
    description: Optional[str] = None
    language: Optional[str] = None
    topics: List[str] = field(default_factory=list)
    stargazers_count: int = 0
    forks_count: int = 0
    homepage: Optional[str] = None
    updated_at: Optional[str] = None
    created_at: Optional[str] = None
    fork: bool = False
    archived: bool = False

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Repo":
        return cls(
            name=data.get("name", ""),
            full_name=data.get("full_name", ""),
            html_url=data.get("html_url", ""),
            description=data.get("description"),
            language=data.get("language"),
            topics=list(data.get("topics") or []),
            stargazers_count=int(data.get("stargazers_count") or 0),
            forks_count=int(data.get("forks_count") or 0),
            homepage=data.get("homepage") or None,
            updated_at=data.get("updated_at"),
            created_at=data.get("created_at"),
            fork=bool(data.get("fork", False)),
            archived=bool(data.get("archived", False)),
        )

    def with_classification(self, classification: "Classification") -> "ClassifiedRepo":
        return ClassifiedRepo(repo=self, classification=classification)


@dataclass
class Assignment:
    """一次归属：类别，以及按简介语言写出的一句简介。"""

    category: str
    summary: str = ""


@dataclass
class Classification:
    category: str
    summary: str = ""


@dataclass
class ClassifiedRepo:
    repo: Repo
    classification: Classification

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self.repo)
        data["category"] = self.classification.category
        if self.classification.summary:
            data["summary"] = self.classification.summary
        return data
