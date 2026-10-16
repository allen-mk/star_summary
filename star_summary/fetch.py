"""星标获取：GitHub 客户端 + 可选缓存。"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .cache import JsonCache


class GitHubClient:
    """PyGithub 薄封装；测试里用 FakeGitHubClient 替换。"""

    def __init__(self, token: str, per_page: int = 100, timeout: int = 30):
        from github import Github, Auth

        self._github = Github(auth=Auth.Token(token), per_page=per_page, timeout=timeout)

    def fetch_all(self) -> List[Dict[str, Any]]:
        user = self._github.get_user()
        repos = []
        for repo in user.get_starred():
            # 列表接口返回的是完整 repo JSON；直接读 _rawData 避免 PyGithub 惰性补全触发每仓库一次请求
            raw = getattr(repo, "_rawData", None) or {}
            repos.append(
                {
                    "id": raw.get("id", repo.id),
                    "name": raw.get("name", repo.name),
                    "full_name": raw.get("full_name", repo.full_name),
                    "description": raw.get("description"),
                    "html_url": raw.get("html_url", repo.html_url),
                    "homepage": raw.get("homepage") or None,
                    "language": raw.get("language"),
                    "topics": list(raw.get("topics") or []),
                    "stargazers_count": raw.get("stargazers_count", 0),
                    "forks_count": raw.get("forks_count", 0),
                    "fork": bool(raw.get("fork", False)),
                    "archived": bool(raw.get("archived", False)),
                    "created_at": raw.get("created_at"),
                    "updated_at": raw.get("updated_at"),
                }
            )
        return repos

    def validate(self) -> Dict[str, Any]:
        user = self._github.get_user()
        rate = self._github.get_rate_limit()
        return {
            "login": user.login,
            "core_remaining": rate.core.remaining,
            "core_limit": rate.core.limit,
        }


def fetch_starred(
    client,
    username: str,
    cache: Optional[JsonCache] = None,
    force_refresh: bool = False,
) -> List[Dict[str, Any]]:
    if cache and not force_refresh:
        cached = cache.load(username)
        if cached is not None:
            return cached
    repos = client.fetch_all()
    if cache:
        cache.save(username, repos)
    return repos
