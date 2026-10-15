import json
from pathlib import Path

from star_summary.fetch import fetch_starred
from star_summary.cache import JsonCache

FIXTURE = Path(__file__).parent / "fixtures" / "starred_sample.json"


class FakeGitHubClient:
    def __init__(self, repos):
        self._repos = repos
        self.calls = 0

    def fetch_all(self):
        self.calls += 1
        return self._repos


def test_fetch_uses_cache_on_second_call(tmp_path):
    raw = json.loads(FIXTURE.read_text(encoding="utf-8"))
    client = FakeGitHubClient(raw)
    cache = JsonCache(tmp_path / "cache")

    first = fetch_starred(client, "user", cache=cache)
    second = fetch_starred(client, "user", cache=cache)

    assert client.calls == 1
    assert len(first) == len(second) == len(raw)


def test_fetch_force_refresh_bypasses_cache(tmp_path):
    raw = json.loads(FIXTURE.read_text(encoding="utf-8"))
    client = FakeGitHubClient(raw)
    cache = JsonCache(tmp_path / "cache")

    fetch_starred(client, "user", cache=cache)
    fetch_starred(client, "user", cache=cache, force_refresh=True)

    assert client.calls == 2
