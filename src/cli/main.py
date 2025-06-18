#!/usr/bin/env python3
"""
GitHub 星标项目分类整理工具 - 主CLI入口文件
基于Click框架的命令行接口
"""

import os
import sys
import json
import shutil
import click
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.config.settings import Config
from src.github_api.service import GitHubService
from src.classifier.classifier import ProjectClassifier
from src.generator.service import DocumentGenerationService
from src.utils.logging import setup_logging, get_logger, LogMessages, ProgressLogger


@click.group()
@click.version_option(version='1.0.0', prog_name='star-summary')
@click.option('--verbose', '-v', is_flag=True, help='启用详细输出')
@click.option('--log-file', default='star_summary.log', help='日志文件路径')
@click.pass_context
def cli(ctx, verbose, log_file):
    """
    🌟 GitHub 星标项目分类整理工具
    
    自动获取、分类和整理您的GitHub星标项目，生成结构清晰的Markdown文档。
    """
    # 设置日志
    logger = setup_logging(verbose=verbose, log_file=log_file)
    
    # 将配置传递给子命令
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['log_file'] = log_file
    ctx.obj['logger'] = logger


@cli.command()
@click.option('--token', envvar='GITHUB_TOKEN', help='GitHub个人访问令牌')
@click.option('--config', default='config.yaml', help='配置文件路径')
@click.option('--output', default='output', help='输出目录')
@click.option('--format', 'output_format', 
              type=click.Choice(['markdown', 'json', 'both']), 
              default='markdown', help='输出格式')
@click.option('--no-cache', is_flag=True, help='禁用缓存')
@click.option('--dry-run', is_flag=True, help='预览模式，显示将要执行的操作')
@click.option('--max-repos', type=int, help='限制处理的项目数量（用于测试）')
@click.pass_context
def generate(ctx, token, config, output, output_format, no_cache, dry_run, max_repos):
    """
    📝 生成星标项目分类文档
    
    获取GitHub星标项目，进行智能分类，并生成结构化的Markdown文档。
    """
    logger = ctx.obj['logger']
    verbose = ctx.obj['verbose']
    
    try:
        logger.info(LogMessages.start_task("生成星标项目分类文档"))
        
        # 验证输入参数
        if not token:
            click.echo("❌ 错误: 需要GitHub Token。请设置GITHUB_TOKEN环境变量或使用--token参数", err=True)
            raise click.Abort()
        
        # 设置token到环境变量（如果通过参数提供）
        if token:
            os.environ['GITHUB_TOKEN'] = token
        
        # 加载配置
        try:
            config_manager = Config(config)
            config_obj = config_manager.config
            logger.info(f"✅ 配置文件加载成功: {config}")
        except Exception as e:
            click.echo(f"❌ 配置文件加载失败: {e}", err=True)
            raise click.Abort()
        
        # 创建输出目录
        output_path = Path(output)
        output_path.mkdir(parents=True, exist_ok=True)
        
        if dry_run:
            _preview_operations(config_obj, output_path, output_format, max_repos)
            return
        
        # 设置缓存
        if no_cache:
            config_obj['cache']['enabled'] = False
            logger.info("🚫 缓存已禁用")
        
        # 执行主要流程
        progress = ProgressLogger(logger, 4)
        
        # 1. 获取星标项目
        progress.step("初始化GitHub服务...")
        github_service = GitHubService(config_manager)
        
        progress.step(LogMessages.fetching_repos("所有"))
        with click.progressbar(label='获取星标项目', length=100) as bar:
            repos = github_service.fetch_starred_repos()
            bar.update(100)
        
        if max_repos and max_repos < len(repos):
            repos = repos[:max_repos]
            logger.info(f"🔢 限制处理项目数量: {max_repos}")
        
        logger.info(f"📊 获取到 {len(repos)} 个星标项目")
        
        # 2. 项目分类
        progress.step(LogMessages.classifying_repos(len(repos)))
        classifier = ProjectClassifier(config_obj)
        
        classified_repos = []
        with click.progressbar(repos, label='分类项目') as repo_bar:
            for repo in repo_bar:
                classified_repo = classifier.classify_repo(repo)
                classified_repos.append(classified_repo)
        
        logger.info(f"✅ 项目分类完成")
        
        # 3. 生成文档
        progress.step(LogMessages.generating_docs(output_format))
        doc_service = DocumentGenerationService(config_manager)
        
        # 生成文档
        result = doc_service.generate_document(classified_repos)
        
        # 4. 保存输出
        progress.step(LogMessages.saving_output(str(output_path)))
        _save_output(result, output_path, output_format, logger)
        
        # 生成摘要
        summary = doc_service.get_generation_summary(result)
        
        progress.complete("文档生成完成")
        click.echo(f"\n✅ 成功生成 {len(repos)} 个项目的分类文档")
        click.echo(f"📊 {summary}")
        click.echo(f"📁 输出目录: {output_path.absolute()}")
        
    except KeyboardInterrupt:
        logger.warning("⚠️ 用户中断操作")
        click.echo("\n❌ 操作已取消")
        raise click.Abort()
    except Exception as e:
        logger.error(LogMessages.error_task("生成文档", str(e)))
        if verbose:
            import traceback
            traceback.print_exc()
        click.echo(f"❌ 执行失败: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.option('--token', envvar='GITHUB_TOKEN', required=True, help='GitHub个人访问令牌')
@click.pass_context
def validate(ctx, token):
    """
    🔍 验证GitHub Token有效性
    
    检查提供的GitHub Token是否有效，并显示API限制信息。
    """
    logger = ctx.obj['logger']
    
    try:
        logger.info(LogMessages.start_task("验证GitHub Token"))
        
        from github import Github
        
        with click.progressbar(length=2, label='验证Token') as bar:
            g = Github(token)
            bar.update(1)
            
            user = g.get_user()
            rate_limit = g.get_rate_limit()
            bar.update(1)
        
        # 显示用户信息
        click.echo(f"✅ Token有效")
        click.echo(f"👤 用户: {user.login}")
        click.echo(f"📧 邮箱: {user.email or '未公开'}")
        click.echo(f"⭐ 公开仓库: {user.public_repos}")
        
        # 显示API限制
        click.echo(f"\n📊 API限制信息:")
        click.echo(f"   核心API: {rate_limit.core.remaining}/{rate_limit.core.limit}")
        click.echo(f"   搜索API: {rate_limit.search.remaining}/{rate_limit.search.limit}")
        
        # 重置时间
        reset_time = rate_limit.core.reset.strftime('%Y-%m-%d %H:%M:%S')
        click.echo(f"   重置时间: {reset_time}")
        
        logger.info("✅ Token验证成功")
        
    except Exception as e:
        logger.error(f"Token验证失败: {e}")
        click.echo(f"❌ Token验证失败: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.argument('output_dir', default='.')
@click.option('--force', is_flag=True, help='强制覆盖现有文件')
@click.pass_context
def init(ctx, output_dir, force):
    """
    🚀 初始化项目配置文件
    
    在指定目录创建配置文件模板和环境变量文件。
    """
    logger = ctx.obj['logger']
    
    try:
        logger.info(LogMessages.start_task("初始化项目配置"))
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 配置文件路径
        config_file = output_path / 'config.yaml'
        env_file = output_path / '.env'
        
        # 检查文件是否存在
        files_exist = []
        if config_file.exists():
            files_exist.append('config.yaml')
        if env_file.exists():
            files_exist.append('.env')
        
        if files_exist and not force:
            click.echo(f"⚠️ 以下文件已存在: {', '.join(files_exist)}")
            click.echo("使用 --force 选项强制覆盖")
            return
        
        # 复制配置模板
        source_config = project_root / 'config.yaml'
        if source_config.exists():
            shutil.copy2(source_config, config_file)
            click.echo(f"✅ 已创建配置文件: {config_file}")
        else:
            logger.warning("源配置文件不存在，创建基本配置")
            _create_basic_config(config_file)
            click.echo(f"✅ 已创建基本配置文件: {config_file}")
        
        # 创建.env模板
        env_content = """# GitHub 星标项目分类整理工具 - 环境变量配置
# 请将 your_token_here 替换为您的GitHub个人访问令牌

GITHUB_TOKEN=your_token_here

# 可选: OpenAI API密钥（用于AI分类功能）
# OPENAI_API_KEY=your_openai_api_key_here
"""
        
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        click.echo(f"✅ 已创建环境变量文件: {env_file}")
        
        # 创建输出目录
        (output_path / 'output').mkdir(exist_ok=True)
        
        click.echo(f"\n🎉 初始化完成！")
        click.echo(f"📁 项目目录: {output_path.absolute()}")
        click.echo(f"\n📝 下一步操作:")
        click.echo(f"   1. 编辑 {env_file} 文件，设置您的GitHub Token")
        click.echo(f"   2. 可选：修改 {config_file} 文件，调整配置")
        click.echo(f"   3. 运行: star-summary generate")
        
        logger.info("✅ 项目初始化完成")
        
    except Exception as e:
        logger.error(f"初始化失败: {e}")
        click.echo(f"❌ 初始化失败: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.option('--config', default='config.yaml', help='配置文件路径')
@click.pass_context
def status(ctx, config):
    """
    📊 显示系统状态和配置信息
    
    检查配置文件、缓存状态和系统信息。
    """
    logger = ctx.obj['logger']
    
    try:
        click.echo("🔍 系统状态检查")
        click.echo("=" * 50)
        
        # 检查配置文件
        config_path = Path(config)
        if config_path.exists():
            click.echo(f"✅ 配置文件: {config_path.absolute()}")
            
            # 加载并显示配置
            try:
                config_manager = Config(config)
                config_obj = config_manager.config
                
                click.echo(f"   输出格式: {config_obj.get('generator', {}).get('default_formats', ['markdown'])}")
                click.echo(f"   缓存启用: {'是' if config_obj.get('cache', {}).get('enabled', True) else '否'}")
                click.echo(f"   分类方法: {config_obj.get('classifier', {}).get('default_method', 'rules')}")
                
            except Exception as e:
                click.echo(f"⚠️ 配置文件格式错误: {e}")
        else:
            click.echo(f"❌ 配置文件不存在: {config_path.absolute()}")
        
        # 检查环境变量
        github_token = os.getenv('GITHUB_TOKEN')
        if github_token:
            click.echo(f"✅ GitHub Token: 已设置 (长度: {len(github_token)})")
        else:
            click.echo("❌ GitHub Token: 未设置")
        
        # 检查缓存目录
        cache_dir = Path('.cache')
        if cache_dir.exists():
            cache_files = list(cache_dir.glob('*'))
            click.echo(f"✅ 缓存目录: {len(cache_files)} 个文件")
        else:
            click.echo("ℹ️ 缓存目录: 不存在")
        
        # 检查依赖
        click.echo("\n📦 依赖检查:")
        dependencies = ['github', 'yaml', 'jinja2', 'click', 'colorama']
        for dep in dependencies:
            try:
                __import__(dep)
                click.echo(f"   ✅ {dep}")
            except ImportError:
                click.echo(f"   ❌ {dep}")
        
        logger.info("状态检查完成")
        
    except Exception as e:
        logger.error(f"状态检查失败: {e}")
        click.echo(f"❌ 状态检查失败: {e}", err=True)


def _preview_operations(config: Dict[str, Any], output_path: Path, 
                       output_format: str, max_repos: Optional[int]):
    """预览将要执行的操作"""
    click.echo("🔍 预览模式 - 将要执行的操作:")
    click.echo("=" * 50)
    click.echo(f"📁 输出目录: {output_path.absolute()}")
    click.echo(f"📄 输出格式: {output_format}")
    click.echo(f"🔢 项目限制: {max_repos or '无限制'}")
    click.echo(f"💾 缓存状态: {'启用' if config.get('cache', {}).get('enabled', True) else '禁用'}")
    click.echo(f"🏷️ 分类方法: {config.get('classifier', {}).get('default_method', 'rules')}")
    
    if output_format in ['markdown', 'both']:
        click.echo(f"   → 将生成: {output_path}/README.md")
    if output_format in ['json', 'both']:
        click.echo(f"   → 将生成: {output_path}/starred_repos.json")


def _save_output(result: Dict[str, Any], output_path: Path, 
                output_format: str, logger):
    """保存输出文件"""
    if output_format in ['markdown', 'both']:
        markdown_file = output_path / 'README.md'
        with open(markdown_file, 'w', encoding='utf-8') as f:
            f.write(result['content']['markdown'])
        logger.info(f"📝 Markdown文档已保存: {markdown_file}")
    
    if output_format in ['json', 'both']:
        json_file = output_path / 'starred_repos.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            # 使用content字段中的json数据，如果没有则使用整个result
            json_data = result['content'].get('json', result)
            json.dump(json_data, f, indent=2, ensure_ascii=False, default=str)
        logger.info(f"📋 JSON数据已保存: {json_file}")


def _create_basic_config(config_file: Path):
    """创建基本配置文件"""
    basic_config = """# GitHub 星标项目分类整理工具配置文件

# GitHub API 配置
github:
  timeout: 30
  retry_count: 3

# 缓存配置
cache:
  enabled: true
  ttl: 3600
  dir: ".cache"

# 分类配置
classifier:
  default_method: "rules"  # rules, ai, hybrid

# 文档生成配置
generator:
  default_formats: ["markdown"]
  template_dir: "templates"
  
# 输出配置
output:
  file_name: "README.md"
  include_toc: true
  include_stats: true
"""
    
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(basic_config)


if __name__ == '__main__':
    cli()
