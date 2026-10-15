"""star-summary 命令行入口。"""

from __future__ import annotations

import sys
from pathlib import Path

import click

from .cache import JsonCache
from .classify import classify_batch
from .config import load_config
from .fetch import GitHubClient, fetch_starred
from .models import Repo
from .render import render_json, render_markdown
from .taxonomy import Taxonomy


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

    out_dir = Path(output or cfg["output"]["base_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    fmt = output_format or cfg["output"]["format"]

    client = _make_client(cfg)
    cache = None if no_cache else _make_cache(cfg)

    click.echo("正在获取星标项目...")
    raw_repos = fetch_starred(client, "me", cache=cache, force_refresh=force_refresh)
    if max_repos:
        raw_repos = raw_repos[:max_repos]
    click.echo(f"获取到 {len(raw_repos)} 个项目")

    taxonomy = Taxonomy.load_default()
    repos = [Repo.from_dict(r) for r in raw_repos]
    items = classify_batch(repos, taxonomy)

    if fmt in ("markdown", "both"):
        md = render_markdown(items, taxonomy)
        path = out_dir / cfg["output"]["markdown_filename"]
        path.write_text(md, encoding="utf-8")
        click.echo(f"Markdown 已保存: {path}")

    if fmt in ("json", "both"):
        js = render_json(items, taxonomy)
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

cache:
  enabled: true
  ttl_hours: 24
  cache_dir: .cache
"""
    target.write_text(template, encoding="utf-8")
    click.echo(f"已创建 {target}，请设置 GITHUB_TOKEN 环境变量后运行: star-summary generate")


if __name__ == "__main__":
    cli()
