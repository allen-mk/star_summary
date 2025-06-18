#!/usr/bin/env python3
"""
CLI子命令定义
扩展的命令行功能和工具命令
"""

import os
import sys
import json
import click
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.config.settings import Config
from src.github_api.service import GitHubService
from src.classifier.classifier import ProjectClassifier
from src.generator.service import DocumentGenerationService
from src.utils.logging import get_logger, LogMessages


@click.group()
def tools():
    """🛠️ 实用工具命令"""
    pass


@tools.command()
@click.option('--token', envvar='GITHUB_TOKEN', required=True, help='GitHub个人访问令牌')
@click.option('--config', default='config.yaml', help='配置文件路径')
@click.option('--format', 'output_format', 
              type=click.Choice(['table', 'json', 'csv']), 
              default='table', help='输出格式')
@click.option('--limit', type=int, default=10, help='显示项目数量限制')
@click.option('--sort-by', type=click.Choice(['stars', 'forks', 'updated', 'name']), 
              default='stars', help='排序方式')
def list_repos(token, config, output_format, limit, sort_by):
    """
    📋 列出星标项目
    
    获取并显示GitHub星标项目列表，支持排序和格式化输出。
    """
    try:
        # 加载配置
        config_manager = Config(config)
        config_obj = config_manager.config
        
        # 初始化GitHub服务
        github_service = GitHubService(config_obj, token)
        
        click.echo("📡 正在获取星标项目...")
        repos = github_service.get_all_starred_repos()
        
        # 排序
        if sort_by == 'stars':
            repos.sort(key=lambda x: x.get('stargazers_count', 0), reverse=True)
        elif sort_by == 'forks':
            repos.sort(key=lambda x: x.get('forks_count', 0), reverse=True)
        elif sort_by == 'updated':
            repos.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
        elif sort_by == 'name':
            repos.sort(key=lambda x: x.get('name', '').lower())
        
        # 限制数量
        if limit > 0:
            repos = repos[:limit]
        
        # 输出
        if output_format == 'table':
            _display_repos_table(repos)
        elif output_format == 'json':
            click.echo(json.dumps(repos, indent=2, ensure_ascii=False, default=str))
        elif output_format == 'csv':
            _display_repos_csv(repos)
        
        click.echo(f"\n📊 共显示 {len(repos)} 个项目")
        
    except Exception as e:
        click.echo(f"❌ 获取项目列表失败: {e}", err=True)
        raise click.Abort()


@tools.command()
@click.option('--token', envvar='GITHUB_TOKEN', required=True, help='GitHub个人访问令牌')
@click.option('--config', default='config.yaml', help='配置文件路径')
@click.option('--method', type=click.Choice(['rules', 'ai', 'hybrid']), 
              default='rules', help='分类方法')
@click.option('--repo-name', help='指定要分类的仓库名称（格式：owner/repo）')
def classify(token, config, method, repo_name):
    """
    🏷️ 测试项目分类
    
    对指定项目或所有星标项目进行分类测试。
    """
    try:
        # 加载配置
        config_manager = Config(config)
        config_obj = config_manager.config
        config_obj['classifier']['default_method'] = method
        
        # 初始化服务
        github_service = GitHubService(config_obj, token)
        classifier = ProjectClassifier(config_obj)
        
        if repo_name:
            # 单个项目分类
            click.echo(f"🔍 正在分析项目: {repo_name}")
            
            # 获取项目信息
            from github import Github
            g = Github(token)
            repo = g.get_repo(repo_name)
            
            repo_data = {
                'name': repo.name,
                'full_name': repo.full_name,
                'description': repo.description,
                'language': repo.language,
                'topics': repo.get_topics(),
                'stargazers_count': repo.stargazers_count,
                'forks_count': repo.forks_count,
                'html_url': repo.html_url,
                'homepage': repo.homepage,
                'created_at': repo.created_at.isoformat(),
                'updated_at': repo.updated_at.isoformat()
            }
            
            # 分类
            result = classifier.classify_repo(repo_data)
            
            # 显示结果
            _display_classification_result(result)
            
        else:
            # 批量分类测试
            click.echo("📡 正在获取星标项目...")
            repos = github_service.get_all_starred_repos()
            
            if len(repos) > 10:
                click.echo(f"⚠️ 项目数量较多 ({len(repos)}个)，仅显示前10个分类结果")
                repos = repos[:10]
            
            # 分类
            results = []
            with click.progressbar(repos, label='分类中') as repo_bar:
                for repo in repo_bar:
                    result = classifier.classify_repo(repo)
                    results.append(result)
            
            # 显示结果摘要
            _display_classification_summary(results)
    
    except Exception as e:
        click.echo(f"❌ 分类测试失败: {e}", err=True)
        raise click.Abort()


@tools.command()
@click.option('--config', default='config.yaml', help='配置文件路径')
@click.option('--template-name', help='指定模板名称')
def template(config, template_name):
    """
    📄 模板管理
    
    查看和管理文档生成模板。
    """
    try:
        # 加载配置
        config_manager = Config(config)
        config_obj = config_manager.config
        
        from src.generator.template import TemplateManager
        
        template_manager = TemplateManager()
        
        if template_name:
            # 显示指定模板
            if template_manager.template_exists(template_name):
                template_path = Path(template_manager.template_dir) / template_name
                click.echo(f"📄 模板: {template_name}")
                click.echo(f"📁 路径: {template_path}")
                click.echo("=" * 50)
                with open(template_path, 'r', encoding='utf-8') as f:
                    click.echo(f.read())
            else:
                click.echo(f"❌ 模板不存在: {template_name}")
        else:
            # 列出所有模板
            templates = template_manager.list_templates()
            
            click.echo("📄 可用模板:")
            click.echo("=" * 50)
            
            for template in templates:
                template_path = Path(template_manager.template_dir) / template
                size = template_path.stat().st_size if template_path.exists() else 0
                click.echo(f"  📄 {template} ({size} bytes)")
            
            click.echo(f"\n📊 共 {len(templates)} 个模板")
    
    except Exception as e:
        click.echo(f"❌ 模板操作失败: {e}", err=True)
        raise click.Abort()


@tools.command()
@click.option('--config', default='config.yaml', help='配置文件路径')
@click.option('--clear', is_flag=True, help='清空缓存')
@click.option('--size', is_flag=True, help='显示缓存大小')
def cache(config, clear, size):
    """
    💾 缓存管理
    
    管理应用程序缓存。
    """
    try:
        # 加载配置
        config_manager = Config(config)
        config_obj = config_manager.config
        
        cache_dir = Path(config_obj.get('cache', {}).get('dir', '.cache'))
        
        if clear:
            # 清空缓存
            if cache_dir.exists():
                import shutil
                shutil.rmtree(cache_dir)
                click.echo("✅ 缓存已清空")
            else:
                click.echo("ℹ️ 缓存目录不存在")
        
        elif size:
            # 显示缓存大小
            if cache_dir.exists():
                total_size = sum(f.stat().st_size for f in cache_dir.rglob('*') if f.is_file())
                file_count = len(list(cache_dir.rglob('*')))
                
                # 格式化大小
                if total_size < 1024:
                    size_str = f"{total_size} B"
                elif total_size < 1024 * 1024:
                    size_str = f"{total_size / 1024:.1f} KB"
                else:
                    size_str = f"{total_size / (1024 * 1024):.1f} MB"
                
                click.echo(f"💾 缓存大小: {size_str}")
                click.echo(f"📁 文件数量: {file_count}")
                click.echo(f"📍 缓存位置: {cache_dir.absolute()}")
            else:
                click.echo("ℹ️ 缓存目录不存在")
        
        else:
            # 显示缓存状态
            enabled = config_obj.get('cache', {}).get('enabled', True)
            ttl = config_obj.get('cache', {}).get('ttl', 3600)
            
            click.echo(f"💾 缓存状态: {'启用' if enabled else '禁用'}")
            click.echo(f"⏰ TTL: {ttl} 秒")
            click.echo(f"📁 缓存目录: {cache_dir.absolute()}")
            
            if cache_dir.exists():
                file_count = len(list(cache_dir.rglob('*')))
                click.echo(f"📄 缓存文件: {file_count} 个")
            else:
                click.echo("📄 缓存文件: 0 个")
    
    except Exception as e:
        click.echo(f"❌ 缓存操作失败: {e}", err=True)
        raise click.Abort()


def _display_repos_table(repos: List[Dict[str, Any]]):
    """以表格形式显示项目列表"""
    if not repos:
        click.echo("📭 没有找到项目")
        return
    
    click.echo("📋 星标项目列表:")
    click.echo("=" * 80)
    
    # 表头
    header = f"{'项目名称':<30} {'语言':<12} {'⭐':<8} {'🍴':<8} {'更新时间':<12}"
    click.echo(header)
    click.echo("-" * 80)
    
    # 项目行
    for repo in repos:
        name = repo.get('name', 'N/A')[:28]
        language = repo.get('language', 'N/A')[:10]
        stars = repo.get('stargazers_count', 0)
        forks = repo.get('forks_count', 0)
        
        # 格式化更新时间
        updated_at = repo.get('updated_at', '')
        if updated_at:
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                updated = dt.strftime('%Y-%m-%d')
            except:
                updated = 'N/A'
        else:
            updated = 'N/A'
        
        row = f"{name:<30} {language:<12} {stars:<8} {forks:<8} {updated:<12}"
        click.echo(row)


def _display_repos_csv(repos: List[Dict[str, Any]]):
    """以CSV格式显示项目列表"""
    if not repos:
        click.echo("name,language,stars,forks,updated_at,url")
        return
    
    # CSV头
    click.echo("name,language,stars,forks,updated_at,url")
    
    # 数据行
    for repo in repos:
        name = repo.get('name', '').replace(',', ';')
        language = repo.get('language', '')
        stars = repo.get('stargazers_count', 0)
        forks = repo.get('forks_count', 0)
        updated = repo.get('updated_at', '')
        url = repo.get('html_url', '')
        
        click.echo(f"{name},{language},{stars},{forks},{updated},{url}")


def _display_classification_result(result: Dict[str, Any]):
    """显示单个项目的分类结果"""
    repo = result['repo']
    classification = result['classification']
    
    click.echo(f"\n📋 项目信息:")
    click.echo(f"  📛 名称: {repo['name']}")
    click.echo(f"  🔗 链接: {repo['html_url']}")
    click.echo(f"  📝 描述: {repo.get('description', '无描述')}")
    click.echo(f"  💻 语言: {repo.get('language', '未知')}")
    click.echo(f"  ⭐ 星数: {repo.get('stargazers_count', 0)}")
    
    if repo.get('topics'):
        click.echo(f"  🏷️ 标签: {', '.join(repo['topics'])}")
    
    click.echo(f"\n🏷️ 分类结果:")
    click.echo(f"  📂 分类: {', '.join(classification['categories'])}")
    click.echo(f"  🔧 方法: {classification['method']}")
    click.echo(f"  📊 置信度: {classification['confidence']:.2f}")
    click.echo(f"  💭 推理: {classification['reasoning']}")


def _display_classification_summary(results: List[Dict[str, Any]]):
    """显示分类结果摘要"""
    if not results:
        click.echo("📭 没有分类结果")
        return
    
    # 统计分类
    category_count = {}
    method_count = {}
    total_confidence = 0
    
    for result in results:
        classification = result['classification']
        
        # 统计分类
        for category in classification['categories']:
            category_count[category] = category_count.get(category, 0) + 1
        
        # 统计方法
        method = classification['method']
        method_count[method] = method_count.get(method, 0) + 1
        
        # 累计置信度
        total_confidence += classification['confidence']
    
    # 显示摘要
    click.echo(f"\n📊 分类摘要 (共 {len(results)} 个项目):")
    click.echo("=" * 50)
    
    click.echo("📂 分类分布:")
    for category, count in sorted(category_count.items(), key=lambda x: x[1], reverse=True):
        click.echo(f"  {category}: {count} 个项目")
    
    click.echo("\n🔧 分类方法:")
    for method, count in method_count.items():
        click.echo(f"  {method}: {count} 个项目")
    
    avg_confidence = total_confidence / len(results)
    click.echo(f"\n📊 平均置信度: {avg_confidence:.2f}")
    
    # 显示前几个分类结果
    click.echo(f"\n📋 详细结果 (前5个):")
    click.echo("-" * 50)
    
    for i, result in enumerate(results[:5]):
        repo = result['repo']
        classification = result['classification']
        click.echo(f"{i+1}. {repo['name']}")
        click.echo(f"   分类: {', '.join(classification['categories'])}")
        click.echo(f"   置信度: {classification['confidence']:.2f}")
        click.echo()


if __name__ == '__main__':
    tools()
