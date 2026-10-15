import os

import pytest

from star_summary.config import load_config


def test_default_config(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cfg = load_config()
    assert cfg["output"]["format"] == "markdown"
    assert cfg["output"]["base_dir"] == "output"
    assert cfg["cache"]["enabled"] is True


def test_config_file_overrides(tmp_path):
    (tmp_path / "config.yaml").write_text("output:\n  format: both\n", encoding="utf-8")
    cfg = load_config(str(tmp_path / "config.yaml"))
    assert cfg["output"]["format"] == "both"


def test_token_from_env(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "abc123")
    cfg = load_config()
    assert cfg["github"]["token"] == "abc123"


def test_missing_token_is_none(monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    cfg = load_config()
    assert cfg["github"]["token"] is None
