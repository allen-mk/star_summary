"""
Markdown文档构建器

负责组织数据和生成Markdown文档
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import defaultdict, Counter

from .template import TemplateManager


logger = logging.getLogger(__name__)


class MarkdownBuilder:
    """
    Markdown文档构建器
    
    负责组织分类数据并生成结构化的Markdown文档
    """
    
    def __init__(self, template_manager: Optional[TemplateManager] = None, 
                 config: Optional[Dict] = None):
        """
        初始化文档构建器
        
        Args:
            template_manager: 模板管理器
            config: 配置信息
        """
        self.template_manager = template_manager or TemplateManager()
        self.config = config or {}
        
        # 确保默认模板存在
        self.template_manager.create_default_templates()
        
        logger.info("Markdown文档构建器初始化完成")
    
    def build_document(self, classified_repos: List[Dict[str, Any]], 
                      template_name: str = 'main.md') -> str:
        """
        构建完整的Markdown文档
        
        Args:
            classified_repos: 分类后的仓库数据列表
            template_name: 使用的模板文件名
            
        Returns:
            生成的Markdown内容
        """
        # 组织数据结构
        organized_data = self.organize_by_categories(classified_repos)
        
        # 生成元数据
        metadata = self.generate_metadata(classified_repos, organized_data)
        
        # 生成目录
        toc = self.generate_toc(organized_data)
        
        # 渲染主文档
        try:
            content = self.template_manager.render_template(
                template_name,
                categories=organized_data,
                metadata=metadata,
                toc=toc
            )
            
            logger.info(f"文档生成成功，包含 {len(classified_repos)} 个项目，{len(organized_data)} 个分类")
            return content
            
        except Exception as e:
            logger.error(f"文档生成失败: {e}")
            raise
    
    def organize_by_categories(self, classified_repos: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        按分类组织仓库数据
        
        Args:
            classified_repos: 分类后的仓库数据列表
            
        Returns:
            按分类组织的数据字典
        """
        categories = defaultdict(lambda: {'repos': [], 'total_stars': 0, 'total_forks': 0})
        
        for repo_data in classified_repos:
            # 新的数据结构：项目数据和分类信息都在同一层级
            classification = repo_data.get('classification', {})
            
            # 获取分类信息
            repo_categories = classification.get('categories', ['uncategorized'])
            
            # 为每个分类添加仓库
            for category in repo_categories:
                # 避免重复添加
                if repo_data not in categories[category]['repos']:
                    categories[category]['repos'].append(repo_data)
                    categories[category]['total_stars'] += repo_data.get('stargazers_count', 0)
                    categories[category]['total_forks'] += repo_data.get('forks_count', 0)
        
        # 按星标数排序每个分类中的仓库
        for category_data in categories.values():
            category_data['repos'].sort(
                key=lambda r: r.get('stargazers_count', 0), 
                reverse=True
            )
        
        # 转换为普通字典并按仓库数量排序
        sorted_categories = dict(sorted(
            categories.items(),
            key=lambda x: len(x[1]['repos']),
            reverse=True
        ))
        
        return sorted_categories
    
    def generate_metadata(self, classified_repos: List[Dict[str, Any]], 
                         organized_data: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        生成文档元数据
        
        Args:
            classified_repos: 分类后的仓库数据列表
            organized_data: 按分类组织的数据
            
        Returns:
            元数据字典
        """
        # 统计总数
        total_count = len(classified_repos)
        category_count = len(organized_data)
        
        # 统计编程语言
        language_counter = Counter()
        category_counter = Counter()
        total_stars = 0
        total_forks = 0
        
        for item in classified_repos:
            repo = item.get('repo', {})
            classification = item.get('classification', {})
            
            # 统计语言
            language = repo.get('language')
            if language:
                language_counter[language] += 1
            
            # 统计分类
            categories = classification.get('categories', ['uncategorized'])
            for category in categories:
                category_counter[category] += 1
            
            # 统计星标和Fork
            total_stars += repo.get('stargazers_count', 0)
            total_forks += repo.get('forks_count', 0)
        
        # 获取前10个最受欢迎的语言和分类
        top_languages = dict(language_counter.most_common(10))
        top_categories = dict(category_counter.most_common(10))
        
        # 找到星标最多的项目
        most_starred = None
        if classified_repos:
            most_starred = max(
                classified_repos,
                key=lambda x: x.get('repo', {}).get('stargazers_count', 0)
            ).get('repo', {})
        
        return {
            'generated_at': datetime.now(),
            'total_count': total_count,
            'category_count': category_count,
            'total_stars': total_stars,
            'total_forks': total_forks,
            'language_stats': top_languages,
            'category_stats': top_categories,
            'most_starred': most_starred,
            'avg_stars': total_stars // total_count if total_count > 0 else 0,
            'avg_forks': total_forks // total_count if total_count > 0 else 0
        }
    
    def generate_toc(self, organized_data: Dict[str, Dict[str, Any]]) -> str:
        """
        生成目录
        
        Args:
            organized_data: 按分类组织的数据
            
        Returns:
            目录Markdown字符串
        """
        try:
            return self.template_manager.render_template('toc.md', categories=organized_data)
        except Exception as e:
            logger.warning(f"使用模板生成目录失败: {e}，使用默认格式")
            
            # 回退到简单格式
            toc_lines = []
            for category_id, category_data in organized_data.items():
                count = len(category_data['repos'])
                # 生成锚点链接
                anchor = self._generate_anchor(category_id)
                toc_lines.append(f"- [{category_id}](#{anchor}) ({count})")
            
            return "\n".join(toc_lines)
    
    def build_category_page(self, category_id: str, repos: List[Dict], 
                           template_name: str = 'category.md') -> str:
        """
        构建单个分类页面
        
        Args:
            category_id: 分类ID
            repos: 该分类下的仓库列表
            template_name: 使用的模板文件名
            
        Returns:
            分类页面Markdown内容
        """
        try:
            return self.template_manager.render_template(
                template_name,
                category_id=category_id,
                repos=repos
            )
        except Exception as e:
            logger.error(f"生成分类页面失败: {e}")
            raise
    
    def build_repo_item(self, repo: Dict[str, Any], 
                       template_name: str = 'repo_item.md') -> str:
        """
        构建单个仓库条目
        
        Args:
            repo: 仓库数据
            template_name: 使用的模板文件名
            
        Returns:
            仓库条目Markdown内容
        """
        try:
            return self.template_manager.render_template(template_name, repo=repo)
        except Exception as e:
            logger.error(f"生成仓库条目失败: {e}")
            raise
    
    def export_data(self, classified_repos: List[Dict[str, Any]], 
                   output_formats: List[str] = None) -> Dict[str, str]:
        """
        导出数据为多种格式
        
        Args:
            classified_repos: 分类后的仓库数据
            output_formats: 输出格式列表，支持 'markdown', 'json'
            
        Returns:
            各格式的内容字典
        """
        if output_formats is None:
            output_formats = ['markdown']
        
        results = {}
        
        if 'markdown' in output_formats:
            results['markdown'] = self.build_document(classified_repos)
        
        if 'json' in output_formats:
            organized_data = self.organize_by_categories(classified_repos)
            metadata = self.generate_metadata(classified_repos, organized_data)
            
            export_data = {
                'metadata': {
                    'generated_at': metadata['generated_at'].isoformat(),
                    'total_count': metadata['total_count'],
                    'category_count': metadata['category_count'],
                    'total_stars': metadata['total_stars'],
                    'total_forks': metadata['total_forks']
                },
                'categories': {}
            }
            
            for category_id, category_data in organized_data.items():
                export_data['categories'][category_id] = {
                    'repos': category_data['repos'],
                    'total_stars': category_data['total_stars'],
                    'total_forks': category_data['total_forks'],
                    'count': len(category_data['repos'])
                }
            
            results['json'] = json.dumps(export_data, indent=2, ensure_ascii=False, default=str)
        
        return results
    
    def _generate_anchor(self, text: str) -> str:
        """
        生成Markdown锚点
        
        Args:
            text: 原始文本
            
        Returns:
            锚点字符串
        """
        # GitHub Markdown锚点生成规则
        anchor = text.lower()
        anchor = anchor.replace(' ', '-')
        anchor = ''.join(c for c in anchor if c.isalnum() or c in '-_')
        return anchor
    
    def get_statistics(self, classified_repos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        获取详细统计信息
        
        Args:
            classified_repos: 分类后的仓库数据
            
        Returns:
            统计信息字典
        """
        organized_data = self.organize_by_categories(classified_repos)
        return self.generate_metadata(classified_repos, organized_data)


class DocumentExporter:
    """
    文档导出器
    
    负责将生成的内容保存到文件
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化文档导出器
        
        Args:
            config: 配置信息
        """
        self.config = config or {}
    
    def export_markdown(self, content: str, output_path: str) -> None:
        """
        导出Markdown文档
        
        Args:
            content: Markdown内容
            output_path: 输出文件路径
        """
        output_file = Path(output_path)
        
        # 创建输出目录
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Markdown文档已保存到: {output_file}")
            
        except Exception as e:
            logger.error(f"保存Markdown文档失败: {e}")
            raise
    
    def export_json(self, data: Any, output_path: str) -> None:
        """
        导出JSON数据
        
        Args:
            data: 要导出的数据
            output_path: 输出文件路径
        """
        output_file = Path(output_path)
        
        # 创建输出目录
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            if isinstance(data, str):
                # 如果已经是JSON字符串，直接写入
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(data)
            else:
                # 否则序列化为JSON
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"JSON数据已保存到: {output_file}")
            
        except Exception as e:
            logger.error(f"保存JSON数据失败: {e}")
            raise
    
    def export_multiple_formats(self, data_dict: Dict[str, str], 
                               base_path: str) -> Dict[str, str]:
        """
        导出多种格式的文件
        
        Args:
            data_dict: 各格式内容字典
            base_path: 基础路径（不含扩展名）
            
        Returns:
            各格式的文件路径字典
        """
        exported_files = {}
        
        for format_name, content in data_dict.items():
            if format_name == 'markdown':
                file_path = f"{base_path}.md"
                self.export_markdown(content, file_path)
            elif format_name == 'json':
                file_path = f"{base_path}.json"
                self.export_json(content, file_path)
            else:
                # 其他格式，使用通用方法
                file_path = f"{base_path}.{format_name}"
                Path(file_path).parent.mkdir(parents=True, exist_ok=True)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"{format_name.upper()}文件已保存到: {file_path}")
            
            exported_files[format_name] = file_path
        
        return exported_files
