"""
文档生成服务

整合分类器和生成器，提供一站式文档生成服务
"""

import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

from ..config.settings import Config
from ..github_api.service import GitHubService
from ..classifier.classifier import ProjectClassifier
from .builder import MarkdownBuilder, DocumentExporter
from .template import TemplateManager


logger = logging.getLogger(__name__)


class DocumentGenerationService:
    """
    文档生成服务
    
    整合GitHub数据获取、项目分类和文档生成功能
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        初始化文档生成服务
        
        Args:
            config: 配置对象，如果为None则从配置文件加载
        """
        if config is None:
            config = Config()
        
        self.config = config
        
        # 初始化组件
        self.github_service = GitHubService(config)
        self.classifier = ProjectClassifier(config)
        self.template_manager = TemplateManager()
        self.builder = MarkdownBuilder(self.template_manager, config.config)
        self.exporter = DocumentExporter(config.config)
        
        logger.info("文档生成服务初始化完成")
    
    def generate_from_github(self, username: Optional[str] = None) -> Dict[str, Any]:
        """
        从GitHub获取星标项目并生成文档
        
        Args:
            username: GitHub用户名，如果为None则从配置中获取
            
        Returns:
            生成结果字典
        """
        try:
            # 获取星标项目
            logger.info("开始获取GitHub星标项目...")
            repos = self.github_service.get_starred_repos(username)
            logger.info(f"成功获取 {len(repos)} 个星标项目")
            
            # 分类项目
            logger.info("开始分类项目...")
            classified_repos = self.classifier.classify_batch(repos, show_progress=True)
            logger.info("项目分类完成")
            
            # 生成文档
            logger.info("开始生成文档...")
            result = self.generate_document(classified_repos)
            logger.info("文档生成完成")
            
            return result
            
        except Exception as e:
            logger.error(f"从GitHub生成文档失败: {e}")
            raise
    
    def generate_document(self, classified_repos: List[Dict[str, Any]], 
                         output_formats: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        生成文档
        
        Args:
            classified_repos: 分类后的仓库数据
            output_formats: 输出格式列表
            
        Returns:
            生成结果字典
        """
        if output_formats is None:
            output_config = self.config.get('output', {})
            format_setting = output_config.get('format', 'markdown')
            
            if format_setting == 'both':
                output_formats = ['markdown', 'json']
            else:
                output_formats = [format_setting]
        
        try:
            # 生成各种格式的内容
            content_dict = self.builder.export_data(classified_repos, output_formats)
            
            # 获取统计信息
            statistics = self.builder.get_statistics(classified_repos)
            
            return {
                'content': content_dict,
                'statistics': statistics,
                'total_repos': len(classified_repos),
                'formats': output_formats
            }
            
        except Exception as e:
            logger.error(f"生成文档失败: {e}")
            raise
    
    def save_document(self, result: Dict[str, Any], 
                     output_path: Optional[str] = None) -> Dict[str, str]:
        """
        保存文档到文件
        
        Args:
            result: 生成结果
            output_path: 输出路径，如果为None则从配置中获取
            
        Returns:
            保存的文件路径字典
        """
        if output_path is None:
            output_config = self.config.get('output', {})
            output_path = output_config.get('paths', {}).get('main_readme', 'README.md')
        
        # 移除扩展名，因为exporter会自动添加
        base_path = str(Path(output_path).with_suffix(''))
        
        try:
            content_dict = result['content']
            saved_files = self.exporter.export_multiple_formats(content_dict, base_path)
            
            logger.info(f"文档已保存，生成了 {len(saved_files)} 个文件")
            return saved_files
            
        except Exception as e:
            logger.error(f"保存文档失败: {e}")
            raise
    
    def generate_and_save(self, username: Optional[str] = None, 
                         output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        一站式生成并保存文档
        
        Args:
            username: GitHub用户名
            output_path: 输出路径
            
        Returns:
            完整的执行结果
        """
        try:
            # 生成文档
            result = self.generate_from_github(username)
            
            # 保存文档
            saved_files = self.save_document(result, output_path)
            
            # 合并结果
            result['saved_files'] = saved_files
            
            return result
            
        except Exception as e:
            logger.error(f"一站式生成文档失败: {e}")
            raise
    
    def generate_category_pages(self, classified_repos: List[Dict[str, Any]], 
                               output_dir: str = 'output/categories') -> Dict[str, str]:
        """
        生成分类页面
        
        Args:
            classified_repos: 分类后的仓库数据
            output_dir: 输出目录
            
        Returns:
            生成的分类页面文件路径字典
        """
        try:
            organized_data = self.builder.organize_by_categories(classified_repos)
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            category_files = {}
            
            for category_id, category_data in organized_data.items():
                # 生成分类页面内容
                content = self.builder.build_category_page(category_id, category_data['repos'])
                
                # 保存到文件
                filename = f"{category_id}.md"
                file_path = output_path / filename
                
                self.exporter.export_markdown(content, str(file_path))
                category_files[category_id] = str(file_path)
            
            logger.info(f"生成了 {len(category_files)} 个分类页面")
            return category_files
            
        except Exception as e:
            logger.error(f"生成分类页面失败: {e}")
            raise
    
    def preview_document(self, classified_repos: List[Dict[str, Any]], 
                        max_repos_per_category: int = 3) -> str:
        """
        预览文档（限制每个分类的项目数量）
        
        Args:
            classified_repos: 分类后的仓库数据
            max_repos_per_category: 每个分类最大显示项目数
            
        Returns:
            预览Markdown内容
        """
        # 创建预览数据（限制项目数量）
        preview_data = []
        category_counts = {}
        
        for item in classified_repos:
            repo = item.get('repo', {})
            classification = item.get('classification', {})
            categories = classification.get('categories', ['uncategorized'])
            
            # 检查是否可以添加到预览
            can_add = False
            for category in categories:
                if category_counts.get(category, 0) < max_repos_per_category:
                    can_add = True
                    break
            
            if can_add:
                preview_data.append(item)
                for category in categories:
                    category_counts[category] = category_counts.get(category, 0) + 1
        
        # 生成预览文档
        return self.builder.build_document(preview_data)
    
    def get_generation_summary(self, result: Dict[str, Any]) -> str:
        """
        获取生成摘要信息
        
        Args:
            result: 生成结果
            
        Returns:
            摘要字符串
        """
        stats = result.get('statistics', {})
        total_repos = result.get('total_repos', 0)
        formats = result.get('formats', [])
        
        summary_lines = [
            f"📊 生成摘要",
            f"- 项目总数: {total_repos}",
            f"- 分类数量: {stats.get('category_count', 0)}",
            f"- 总星标数: {stats.get('total_stars', 0):,}",
            f"- 输出格式: {', '.join(formats)}",
        ]
        
        if 'language_stats' in stats:
            summary_lines.append(f"- 主要语言: {', '.join(list(stats['language_stats'].keys())[:5])}")
        
        return "\n".join(summary_lines)
