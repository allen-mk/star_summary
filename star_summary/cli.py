"""star-summary 命令行入口。"""

from __future__ import annotations

import sys
from pathlib import Path

import click

from .brief import load_brief, resolve_category
from .cache import JsonCache
from .config import load_config, model_env_names, model_ready
from .fetch import GitHubClient, fetch_starred
from .model import ModelClient, ModelError
from .models import Assignment, Classification, Repo
from .render import render_json, render_markdown


@click.group()
@click.version_option(version="2.0.0", prog_name="star-summary")
def cli():
    """GitHub 星标项目分类整理工具。"""


def _make_client(cfg):
    return GitHubClient(
        token=cfg["github"]["token"],
        per_page=cfg["github"].get("per_page", 100),
        timeout=cfg["github"].get("timeout", 30),
    )


def _output_plan(output_format, output_cfg):
    """命令行 --format 优先，否则用 output.format。markdown 只写目录，both 两份都写，json 只写分类数据。"""
    fmt = output_format or output_cfg.get("format") or "markdown"
    return fmt in ("markdown", "both"), fmt in ("json", "both")


def _make_cache(cfg):
    cache_cfg = cfg.get("cache", {})
    if not cache_cfg.get("enabled", True):
        return None
    return JsonCache(cache_cfg.get("cache_dir", ".cache"), ttl_hours=cache_cfg.get("ttl_hours", 24))


@cli.command()
@click.option("--config", "config_path", default=None, help="配置文件路径")
@click.option("--output", default=None, help="输出目录")
@click.option("--format", "output_format", type=click.Choice(["markdown", "json", "both"]), default=None)
@click.option("--no-cache", is_flag=True, help="禁用缓存")
@click.option("--force-refresh", is_flag=True, help="忽略缓存强制拉取")
@click.option("--max-repos", type=int, default=None, help="限制处理项目数量（测试用）")
def generate(config_path, output, output_format, no_cache, force_refresh, max_repos):
    """生成星标项目分类文档。"""
    cfg = load_config(config_path)
    if not cfg["github"]["token"]:
        click.echo("错误: 需要 GitHub Token，请设置 GITHUB_TOKEN 环境变量", err=True)
        sys.exit(1)
    if not model_ready(cfg):
        base_env, key_env, name_env = model_env_names(cfg)
        click.echo(f"错误: 需要模型接入，请设置 {base_env}、{key_env} 和 {name_env}", err=True)
        sys.exit(1)

    out_dir = Path(output or cfg["output"]["base_dir"])
    write_md, write_json = _output_plan(output_format, cfg["output"])

    client = _make_client(cfg)
    cache = None if no_cache else _make_cache(cfg)

    click.echo("正在获取星标项目...")
    raw_repos = fetch_starred(client, "me", cache=cache, force_refresh=force_refresh)
    if max_repos:
        raw_repos = raw_repos[:max_repos]
    click.echo(f"获取到 {len(raw_repos)} 个项目")

    brief = load_brief(cfg.get("brief_path") or "classify.yaml")
    repos = [Repo.from_dict(r) for r in raw_repos]
    model_cfg = cfg["model"]
    model = ModelClient(
        base_url=model_cfg["base_url"],
        api_key=model_cfg["api_key"],
        model=model_cfg["model"],
        timeout=int(model_cfg.get("timeout") or 60),
    )
    language = str(cfg["output"].get("description_language") or "").strip().lower()
    try:
        assigned = model.assign(brief, repos, description_language=language)
    except ModelError as exc:
        click.echo(f"错误: {exc}", err=True)
        sys.exit(1)
    items = []
    for repo in repos:
        value = assigned[repo.full_name]
        if isinstance(value, Assignment):
            category, summary = value.category, value.summary
        else:
            category, summary = value, ""
        items.append(
            repo.with_classification(
                Classification(category=resolve_category(category, brief), summary=summary)
            )
        )
    out_dir.mkdir(parents=True, exist_ok=True)

    if write_md:
        md = render_markdown(items, brief)
        path = out_dir / cfg["output"]["markdown_filename"]
        path.write_text(md, encoding="utf-8")
        click.echo(f"Markdown 已保存: {path}")

    if write_json:
        js = render_json(items)
        path = out_dir / cfg["output"]["json_filename"]
        path.write_text(js, encoding="utf-8")
        click.echo(f"JSON 已保存: {path}")

    click.echo(f"完成，输出目录: {out_dir.absolute()}")


@cli.command()
@click.option("--config", "config_path", default=None, help="配置文件路径")
def validate(config_path):
    """验证 GitHub Token 有效性。"""
    cfg = load_config(config_path)
    if not cfg["github"]["token"]:
        click.echo("错误: 需要 GitHub Token，请设置 GITHUB_TOKEN 环境变量", err=True)
        sys.exit(1)
    client = _make_client(cfg)
    info = client.validate()
    click.echo(f"Token 有效，用户: {info['login']}")
    click.echo(f"API 配额: {info['core_remaining']}/{info['core_limit']}")


@cli.command()
@click.option("--force", is_flag=True, help="覆盖已存在的 config.yaml")
def init(force):
    """在当前目录创建配置文件模板。"""
    target = Path("config.yaml")
    if target.exists() and not force:
        click.echo("config.yaml 已存在，使用 --force 覆盖")
        return
    template = """# star-summary 配置
output:
  format: markdown   # markdown | json | both
  base_dir: output
  description_language: ""  # 留空用原描述。语言代号如 zh-cn、en

cache:
  enabled: true
  ttl_hours: 24
  cache_dir: .cache

model:
  base_url_env: STAR_SUMMARY_BASE_URL
  api_key_env: STAR_SUMMARY_API_KEY
  model_env: STAR_SUMMARY_MODEL

brief_path: classify.yaml
"""
    target.write_text(template, encoding="utf-8")
    click.echo(
        f"已创建 {target}，请设置 GITHUB_TOKEN、STAR_SUMMARY_BASE_URL、STAR_SUMMARY_API_KEY 和 STAR_SUMMARY_MODEL 后运行: star-summary generate"
    )


if __name__ == "__main__":
    cli()
