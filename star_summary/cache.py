"""简单的 JSON 文件缓存。"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, List, Optional


class JsonCache:
    def __init__(self, cache_dir, ttl_hours: float = 24):
        self.cache_dir = Path(cache_dir)
        self.ttl_seconds = ttl_hours * 3600
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, username: str) -> Path:
        safe = username.replace("/", "_")
        return self.cache_dir / f"starred_{safe}.json"

    def save(self, username: str, repos: List[dict]) -> None:
        payload = {"cached_at": time.time(), "repos": repos}
        self._path(username).write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    def load(self, username: str) -> Optional[List[dict]]:
        path = self._path(username)
        if not path.exists():
            return None
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None
        if self.ttl_seconds <= 0:
            return None
        if time.time() - payload.get("cached_at", 0) > self.ttl_seconds:
            return None
        return payload.get("repos")

    def clear(self, username: str) -> None:
        path = self._path(username)
        if path.exists():
            path.unlink()
