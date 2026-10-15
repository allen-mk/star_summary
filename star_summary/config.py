"""配置加载：单一 schema，代码只读不写。"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

DEFAULT_CONFIG: Dict[str, Any] = {
    "github": {
        "token_env": "GITHUB_TOKEN",
        "timeout": 30,
        "per_page": 100,
    },
    "output": {
        "format": "both",  # markdown | json | both
        "base_dir": "output",
        "markdown_filename": "README.md",
        "json_filename": "starred_repos.json",
        "description_language": "",
    },
    "cache": {
        "enabled": True,
        "ttl_hours": 24,
        "cache_dir": ".cache",
    },
    "logging": {
        "level": "INFO",
    },
    "model": {
        "base_url_env": "STAR_SUMMARY_BASE_URL",
        "api_key_env": "STAR_SUMMARY_API_KEY",
        "model_env": "STAR_SUMMARY_MODEL",
    },
    "brief_path": "classify.yaml",
}


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    result = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_config(path: Optional[str] = None) -> Dict[str, Any]:
    """加载配置；文件不存在时使用默认值，不写盘。"""
    cfg = DEFAULT_CONFIG
    config_path = Path(path) if path else Path("config.yaml")
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            user_cfg = yaml.safe_load(f) or {}
        cfg = _deep_merge(DEFAULT_CONFIG, user_cfg)

    cfg = dict(cfg)
    cfg["github"] = dict(cfg["github"])
    token_env = cfg["github"].get("token_env", "GITHUB_TOKEN")
    cfg["github"]["token"] = os.getenv(token_env)
    cfg["model"] = dict(cfg.get("model") or {})
    # 文件里的地址和模型名一律不用，避免写进仓库后泄露。
    cfg["model"].pop("base_url", None)
    cfg["model"].pop("model", None)
    base_env, key_env, name_env = model_env_names(cfg)
    cfg["model"]["base_url_env"] = base_env
    cfg["model"]["api_key_env"] = key_env
    cfg["model"]["model_env"] = name_env
    cfg["model"]["base_url"] = _env_value(base_env)
    cfg["model"]["api_key"] = _env_value(key_env)
    cfg["model"]["model"] = _env_value(name_env)
    return cfg


def model_env_names(cfg: Dict[str, Any]):
    model = cfg.get("model") or {}
    return (
        str(model.get("base_url_env") or "STAR_SUMMARY_BASE_URL"),
        str(model.get("api_key_env") or "STAR_SUMMARY_API_KEY"),
        str(model.get("model_env") or "STAR_SUMMARY_MODEL"),
    )


def _env_value(name: str):
    if not name:
        return None
    value = (os.getenv(name) or "").strip()
    return value or None


def model_ready(cfg: Dict[str, Any]) -> bool:
    model = cfg.get("model") or {}
    return bool(model.get("base_url") and model.get("api_key") and model.get("model"))
