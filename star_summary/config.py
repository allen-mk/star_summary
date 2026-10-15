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
        "format": "markdown",  # markdown | json | both
        "base_dir": "output",
        "markdown_filename": "README.md",
        "json_filename": "starred_repos.json",
    },
    "cache": {
        "enabled": True,
        "ttl_hours": 24,
        "cache_dir": ".cache",
    },
    "logging": {
        "level": "INFO",
    },
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
    return cfg
