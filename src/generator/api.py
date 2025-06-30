"""
JSON API数据生成器

为前端开发提供标准化的JSON数据接口
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Set
from pathlib import Path

logger = logging.getLogger(__name__)


class DataAPI:
    """
    数据API生成器
    
    将分类后的仓库数据转换为标准化的JSON API格式
    为前端开发提供结构化的数据接口
    """
    
    def __init__(self, classified_repos: List[Dict[str, Any]]):
        """
        初始化数据API生成器
        
        Args:
            classified_repos: 分类后的仓库数据列表
        """
        self.repos = classified_repos
        self.version = "1.0.0"
        
        logger.info(f"DataAPI初始化完成，包含 {len(self.repos)} 个项目")
    
    def get_all_categories(self) -> Set[str]:
        """
        获取所有分类
        
        Returns:
            所有分类的集合
        """
        categories = set()
        for repo in self.repos:
            classification = repo.get('classification', {})
            repo_categories = classification.get('categories', [])
            categories.update(repo_categories)
        
        return categories
    
    def get_all_languages(self) -> Set[str]:
        """
        获取所有编程语言
        
        Returns:
            所有编程语言的集合
        """
        languages = set()
        for repo in self.repos:
            language = repo.get('language')
            if language:
                languages.add(language)
        
        return languages
    
    def generate_stats(self) -> Dict[str, Any]:
        """
        生成统计信息
        
        Returns:
            统计数据字典
        """
        total_stars = sum(repo.get('stargazers_count', 0) for repo in self.repos)
        total_forks = sum(repo.get('forks_count', 0) for repo in self.repos)
        
        # 按分类统计
        category_stats = {}
        for repo in self.repos:
            classification = repo.get('classification', {})
            categories = classification.get('categories', ['uncategorized'])
            for category in categories:
                if category not in category_stats:
                    category_stats[category] = {
                        'count': 0,
                        'total_stars': 0,
                        'total_forks': 0
                    }
                category_stats[category]['count'] += 1
                category_stats[category]['total_stars'] += repo.get('stargazers_count', 0)
                category_stats[category]['total_forks'] += repo.get('forks_count', 0)
        
        # 按语言统计
        language_stats = {}
        for repo in self.repos:
            language = repo.get('language', 'Unknown')
            if language not in language_stats:
                language_stats[language] = {
                    'count': 0,
                    'total_stars': 0,
                    'total_forks': 0
                }
            language_stats[language]['count'] += 1
            language_stats[language]['total_stars'] += repo.get('stargazers_count', 0)
            language_stats[language]['total_forks'] += repo.get('forks_count', 0)
        
        # 最受欢迎的项目
        most_starred = max(self.repos, key=lambda x: x.get('stargazers_count', 0), default={})
        most_forked = max(self.repos, key=lambda x: x.get('forks_count', 0), default={})
        
        return {
            'total_repositories': len(self.repos),
            'total_stars': total_stars,
            'total_forks': total_forks,
            'total_categories': len(self.get_all_categories()),
            'total_languages': len(self.get_all_languages()),
            'avg_stars': total_stars / len(self.repos) if self.repos else 0,
            'avg_forks': total_forks / len(self.repos) if self.repos else 0,
            'categories': category_stats,
            'languages': language_stats,
            'most_starred': {
                'name': most_starred.get('name', ''),
                'full_name': most_starred.get('full_name', ''),
                'stars': most_starred.get('stargazers_count', 0),
                'url': most_starred.get('html_url', '')
            },
            'most_forked': {
                'name': most_forked.get('name', ''),
                'full_name': most_forked.get('full_name', ''),
                'forks': most_forked.get('forks_count', 0),
                'url': most_forked.get('html_url', '')
            }
        }
    
    def generate_api_data(self) -> Dict[str, Any]:
        """
        生成完整的API数据
        
        Returns:
            标准化的JSON API数据格式
        """
        try:
            metadata = {
                'generated_at': datetime.now().isoformat(),
                'version': self.version,
                'total_repos': len(self.repos),
                'categories': list(self.get_all_categories()),
                'languages': list(self.get_all_languages()),
                'stats': self.generate_stats()
            }
            
            repositories = []
            for repo in self.repos:
                classification = repo.get('classification', {})
                
                # 处理日期字段
                created_at = repo.get('created_at')
                updated_at = repo.get('updated_at')
                pushed_at = repo.get('pushed_at')
                
                if isinstance(created_at, str):
                    created_at_iso = created_at
                elif hasattr(created_at, 'isoformat'):
                    created_at_iso = created_at.isoformat()
                else:
                    created_at_iso = None
                
                if isinstance(updated_at, str):
                    updated_at_iso = updated_at
                elif hasattr(updated_at, 'isoformat'):
                    updated_at_iso = updated_at.isoformat()
                else:
                    updated_at_iso = None
                
                if isinstance(pushed_at, str):
                    pushed_at_iso = pushed_at
                elif hasattr(pushed_at, 'isoformat'):
                    pushed_at_iso = pushed_at.isoformat()
                elif pushed_at is None:
                    pushed_at_iso = None
                else:
                    pushed_at_iso = None
                
                repo_data = {
                    'id': repo.get('id'),
                    'name': repo.get('name'),
                    'full_name': repo.get('full_name'),
                    'description': repo.get('description'),
                    'html_url': repo.get('html_url'),
                    'clone_url': repo.get('clone_url'),
                    'ssh_url': repo.get('ssh_url'),
                    'homepage': repo.get('homepage'),
                    'language': repo.get('language'),
                    'stargazers_count': repo.get('stargazers_count', 0),
                    'forks_count': repo.get('forks_count', 0),
                    'watchers_count': repo.get('watchers_count', 0),
                    'open_issues_count': repo.get('open_issues_count', 0),
                    'size': repo.get('size', 0),
                    'topics': repo.get('topics', []),
                    'license': repo.get('license'),
                    'private': repo.get('private', False),
                    'fork': repo.get('fork', False),
                    'archived': repo.get('archived', False),
                    'disabled': repo.get('disabled', False),
                    'created_at': created_at_iso,
                    'updated_at': updated_at_iso,
                    'pushed_at': pushed_at_iso,
                    'owner': repo.get('owner'),
                    # 分类信息
                    'categories': classification.get('categories', []),
                    'classification_method': classification.get('method', 'unknown'),
                    'classification_confidence': classification.get('confidence', 0.0),
                    'classification_reasoning': classification.get('reasoning', '')
                }
                
                repositories.append(repo_data)
            
            api_data = {
                'metadata': metadata,
                'repositories': repositories
            }
            
            logger.info(f"API数据生成完成，包含 {len(repositories)} 个项目")
            return api_data
            
        except Exception as e:
            logger.error(f"生成API数据时出错: {e}")
            raise
    
    def save_api_data(self, output_path: str) -> str:
        """
        保存API数据到文件
        
        Args:
            output_path: 输出文件路径
            
        Returns:
            实际保存的文件路径
        """
        try:
            data = self.generate_api_data()
            
            # 确保输出目录存在
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            
            file_size = output_file.stat().st_size
            logger.info(f"API数据已保存到: {output_file.absolute()} ({file_size} bytes)")
            
            return str(output_file.absolute())
            
        except Exception as e:
            logger.error(f"保存API数据时出错: {e}")
            raise
    
    def get_api_summary(self) -> Dict[str, Any]:
        """
        获取API数据摘要
        
        Returns:
            API数据摘要信息
        """
        stats = self.generate_stats()
        
        return {
            'total_repositories': len(self.repos),
            'total_categories': len(self.get_all_categories()),
            'total_languages': len(self.get_all_languages()),
            'total_stars': stats['total_stars'],
            'total_forks': stats['total_forks'],
            'most_popular_language': max(
                stats['languages'].items(),
                key=lambda x: x[1]['count'],
                default=('Unknown', {'count': 0})
            )[0],
            'most_popular_category': max(
                stats['categories'].items(),
                key=lambda x: x[1]['count'],
                default=('uncategorized', {'count': 0})
            )[0]
        }
