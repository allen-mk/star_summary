import json
import time

from star_summary.cache import JsonCache


def test_cache_roundtrip(tmp_path):
    cache = JsonCache(tmp_path / "cache")
    repos = [{"full_name": "a/b"}]
    cache.save("user", repos)
    assert cache.load("user") == repos


def test_cache_miss_returns_none(tmp_path):
    cache = JsonCache(tmp_path / "cache")
    assert cache.load("nobody") is None


def test_cache_expiry(tmp_path):
    cache = JsonCache(tmp_path / "cache", ttl_hours=0)
    cache.save("user", [{"full_name": "a/b"}])
    # ttl 0 视为立即过期
    assert cache.load("user") is None


def test_cache_clear(tmp_path):
    cache = JsonCache(tmp_path / "cache")
    cache.save("user", [{"full_name": "a/b"}])
    cache.clear("user")
    assert cache.load("user") is None
