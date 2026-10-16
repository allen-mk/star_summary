"""模型接入：只走 OpenAI Chat Completions。"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Dict, List

from .brief import Brief
from .models import Assignment


class ModelError(Exception):
    """模型没有返回可解析的完整归属。"""


class ModelClient:
    def __init__(self, base_url: str, api_key: str, model: str, timeout: int = 60):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout = timeout

    def assign(self, brief: Brief, repos, description_language: str = "") -> Dict[str, Assignment]:
        found: Dict[str, Assignment] = {}
        step = 20 if description_language else 40
        for start in range(0, len(repos), step):
            chunk = repos[start : start + step]
            content = self.complete(_messages(brief, chunk, description_language))
            found.update(_parse_assignments(content, chunk, description_language))
        return found

    def complete(self, messages: List[dict]) -> str:
        payload = {"model": self.model, "messages": messages, "max_tokens": 4096}
        # 推理模型会把额度花在 reasoning_content 上，分类只需要正文里的 JSON。
        payload["thinking"] = {"type": "disabled"}
        try:
            return self._post(payload)
        except urllib.error.HTTPError as exc:
            if exc.code != 400:
                raise ModelError("模型没有返回可解析的归属") from exc
            payload.pop("thinking", None)
            try:
                return self._post(payload)
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as retry_exc:
                raise ModelError("模型没有返回可解析的归属") from retry_exc

    def _post(self, payload: dict) -> str:
        url = f"{self.base_url}/chat/completions"
        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError:
            raise
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise ModelError("模型没有返回可解析的归属") from exc
        try:
            content = body["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ModelError("模型没有返回可解析的归属") from exc
        if not content:
            raise ModelError("模型没有返回可解析的归属")
        return content


def _messages(brief: Brief, repos, description_language: str = "") -> List[dict]:
    categories = "\n".join(f"- {item.name}: {item.description}" for item in brief.categories)
    stars = "\n".join(
        f"- {repo.full_name} | {repo.description or ''} | {repo.language or ''} | {', '.join(repo.topics)}"
        for repo in repos
    )
    if description_language:
        summary_rule = (
            f"简介语言代号是 {description_language}。"
            "summary 用这个语言写一句简介：有描述就依据描述，没有就依据仓库名和 topics。"
            "不要翻译仓库名。\n\n"
        )
        shape = (
            '{"assignments": [{"full_name": "owner/name", "category": "类别名", "summary": "一句简介"}]}'
        )
    else:
        summary_rule = ""
        shape = '{"assignments": [{"full_name": "owner/name", "category": "类别名"}]}'
    user = (
        "为每个星标选择恰好一个类别。只能使用列出的类别名。没有合适类别时使用未归类。\n\n"
        f"{summary_rule}"
        f"类别：\n{categories}\n\n"
        f"偏好：\n{brief.preferences or '无'}\n\n"
        f"硬性规则：\n{brief.hard_rules or '无'}\n\n"
        f"星标（仓库名 | 描述 | 语言 | topics）：\n{stars}\n\n"
        f"只返回 JSON：{shape}。"
        "必须覆盖上面每一个星标。"
    )
    return [
        {"role": "system", "content": "你只根据给定材料做归属，并只返回 JSON。"},
        {"role": "user", "content": user},
    ]


def _parse_assignments(content: str, repos, description_language: str = "") -> Dict[str, Assignment]:
    start = content.find("{")
    end = content.rfind("}")
    if start < 0 or end < start:
        raise ModelError("模型没有返回可解析的归属")
    try:
        data = json.loads(content[start : end + 1])
    except json.JSONDecodeError as exc:
        raise ModelError("模型没有返回可解析的归属") from exc
    rows = data.get("assignments") if isinstance(data, dict) else None
    if not isinstance(rows, list):
        raise ModelError("模型没有返回可解析的归属")
    found: Dict[str, Assignment] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ModelError("模型没有返回可解析的归属")
        full_name = row.get("full_name")
        category = row.get("category")
        summary = row.get("summary") or ""
        if not isinstance(full_name, str) or not isinstance(category, str) or not isinstance(summary, str):
            raise ModelError("模型没有返回可解析的归属")
        summary = summary.strip()
        if description_language and not summary:
            raise ModelError("模型没有返回可解析的归属")
        found[full_name] = Assignment(category=category, summary=summary if description_language else "")
    expected = {repo.full_name for repo in repos}
    if set(found) != expected:
        raise ModelError("模型没有返回可解析的归属")
    return found
