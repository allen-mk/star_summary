import os

import pytest

from star_summary.config import load_config, model_ready


def test_default_config(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cfg = load_config()
    assert cfg["output"]["format"] == "both"
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


def test_model_values_come_from_env_not_file(tmp_path, monkeypatch):
    monkeypatch.setenv("STAR_SUMMARY_BASE_URL", "https://example.test/v1")
    monkeypatch.setenv("STAR_SUMMARY_API_KEY", "secret-key")
    monkeypatch.setenv("STAR_SUMMARY_MODEL", "fake-model")
    (tmp_path / "config.yaml").write_text(
        "model:\n  base_url: https://leaked.example/v1\n  model: leaked-model\n",
        encoding="utf-8",
    )
    cfg = load_config(str(tmp_path / "config.yaml"))
    assert cfg["model"]["base_url"] == "https://example.test/v1"
    assert cfg["model"]["api_key"] == "secret-key"
    assert cfg["model"]["model"] == "fake-model"
    assert model_ready(cfg)


def test_model_missing_env_is_not_ready(monkeypatch):
    monkeypatch.delenv("STAR_SUMMARY_BASE_URL", raising=False)
    monkeypatch.delenv("STAR_SUMMARY_API_KEY", raising=False)
    monkeypatch.delenv("STAR_SUMMARY_MODEL", raising=False)
    cfg = load_config()
    assert cfg["model"]["base_url"] is None
    assert cfg["model"]["api_key"] is None
    assert cfg["model"]["model"] is None
    assert not model_ready(cfg)
