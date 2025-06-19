"""
智能项目分类器

主分类器类，统一管理不同的分类方式
"""

import logging
import os
from typing import Dict, List, Any, Optional, Union

from .rules import RuleEngine
from .ai_classifier import AIClassifier
from .hybrid_classifier import HybridClassifier
from .categories import CategoryManager


logger = logging.getLogger(__name__)


class ProjectClassifier:
    """
    项目分类器主类
    
    根据配置选择合适的分类方式（规则、AI或混合）
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化项目分类器
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.category_manager = CategoryManager()
        
        # 获取分类方法
        classification_config = config.get('classification', {})
        self.method = classification_config.get('method', 'rules').lower()
        
        # 初始化对应的分类器
        self.classifier = self._create_classifier()
        
        logger.info(f"项目分类器初始化完成，使用方法: {self.method}")
    
    def _create_classifier(self) -> Union[RuleEngine, AIClassifier, HybridClassifier]:
        """
        根据配置创建分类器
        
        Returns:
            分类器实例
        """
        if self.method == 'ai':
            return self._create_ai_classifier()
        elif self.method == 'hybrid':
            return self._create_hybrid_classifier()
        else:  # 默认使用规则分类
            return self._create_rule_classifier()
    
    def _create_rule_classifier(self) -> RuleEngine:
        """
        创建规则分类器
        
        Returns:
            规则引擎实例
        """
        rule_engine = RuleEngine()
        rule_engine.setup_default_rules()
        logger.info(f"规则分类器创建完成，加载了 {len(rule_engine.rules)} 条规则")
        return rule_engine
    
    def _create_ai_classifier(self) -> AIClassifier:
        """
        创建AI分类器
        
        Returns:
            AI分类器实例
        """
        ai_config = self.config.get('ai_classification', {})
        
        # 获取API密钥
        api_key = self._get_api_key(ai_config)
        if not api_key:
            raise ValueError("未配置OpenAI API密钥，无法使用AI分类")
        
        model = ai_config.get('model', 'gpt-3.5-turbo')
        
        ai_classifier = AIClassifier(
            api_key=api_key,
            model=model,
            category_manager=self.category_manager
        )
        
        logger.info(f"AI分类器创建完成，使用模型: {model}")
        return ai_classifier
    
    def _create_hybrid_classifier(self) -> HybridClassifier:
        """
        创建混合分类器
        
        Returns:
            混合分类器实例
        """
        hybrid_classifier = HybridClassifier(self.config)
        logger.info("混合分类器创建完成")
        return hybrid_classifier
    
    def _get_api_key(self, ai_config: Dict[str, Any]) -> Optional[str]:
        """
        获取API密钥
        
        Args:
            ai_config: AI配置
            
        Returns:
            API密钥
        """
        # 从配置中直接获取
        if 'api_key' in ai_config:
            return ai_config['api_key']
        
        # 从环境变量获取
        env_var = ai_config.get('api_key_env', 'OPENAI_API_KEY')
        return os.getenv(env_var)
    
    def classify_repo(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分类单个项目
        
        Args:
            repo_data: 项目数据
            
        Returns:
            包含项目数据和分类结果的字典
        """
        try:
            # 复制原始项目数据
            result = repo_data.copy()
            
            if hasattr(self.classifier, 'classify_repo'):
                classification = self.classifier.classify_repo(repo_data)
            else:
                # 对于RuleEngine，使用classify方法
                categories = self.classifier.classify(repo_data)
                classification = {
                    'categories': categories,
                    'method': 'rules',
                    'confidence': 0.8,
                    'reasoning': '基于预定义规则分类'
                }
            
            # 添加分类信息到项目数据
            result['classification'] = classification
            return result
            
        except Exception as e:
            logger.error(f"分类项目 {repo_data.get('name', 'Unknown')} 时出错: {e}")
            # 即使分类失败，也返回原始数据和默认分类
            result = repo_data.copy()
            result['classification'] = {
                'categories': ['uncategorized'],
                'method': 'error',
                'confidence': 0.0,
                'reasoning': f'分类出错: {str(e)}',
                'error': str(e)
            }
            return result
    
    def classify_batch(self, repos: List[Dict[str, Any]], 
                      show_progress: bool = True) -> List[Dict[str, Any]]:
        """
        批量分类项目
        
        Args:
            repos: 项目列表
            show_progress: 是否显示进度条
            
        Returns:
            分类结果列表
        """
        # 如果分类器有批量分类方法，直接使用
        if hasattr(self.classifier, 'classify_batch'):
            return self.classifier.classify_batch(repos, show_progress)
        
        # 否则逐个分类
        results = []
        
        if show_progress:
            try:
                from tqdm import tqdm
                iterator = tqdm(repos, desc=f"分类项目({self.method})", unit="项目")
            except ImportError:
                logger.warning("未安装tqdm，将不显示进度条")
                iterator = repos
        else:
            iterator = repos
        
        for repo in iterator:
            classification = self.classify_repo(repo)
            results.append({
                'repo': repo,
                'classification': classification
            })
        
        return results
    
    def get_supported_categories(self) -> Dict[str, Dict[str, str]]:
        """
        获取支持的分类体系
        
        Returns:
            分类体系字典
        """
        return self.category_manager.categories
    
    def validate_classification_result(self, result: Dict[str, Any]) -> bool:
        """
        验证分类结果的有效性
        
        Args:
            result: 分类结果
            
        Returns:
            是否有效
        """
        required_fields = ['categories', 'method', 'confidence']
        
        # 检查必需字段
        for field in required_fields:
            if field not in result:
                logger.error(f"分类结果缺少必需字段: {field}")
                return False
        
        # 检查分类是否有效
        categories = result['categories']
        if not isinstance(categories, list) or not categories:
            logger.error("分类结果必须是非空列表")
            return False
        
        # 检查分类是否在支持的范围内
        for category in categories:
            if not self.category_manager.is_valid_category(category):
                logger.warning(f"分类结果包含无效分类: {category}")
        
        # 检查置信度
        confidence = result['confidence']
        if not isinstance(confidence, (int, float)) or not (0 <= confidence <= 1):
            logger.error("置信度必须是0-1之间的数值")
            return False
        
        return True
    
    def export_classification_rules(self) -> Dict[str, Any]:
        """
        导出分类规则配置
        
        Returns:
            规则配置字典
        """
        if hasattr(self.classifier, 'rule_engine'):
            rule_engine = self.classifier.rule_engine
        elif isinstance(self.classifier, RuleEngine):
            rule_engine = self.classifier
        else:
            return {}
        
        rules_config = []
        for rule in rule_engine.rules:
            rules_config.append({
                'name': rule.name,
                'category': rule.category,
                'priority': rule.priority,
                'description': rule.description
            })
        
        return {
            'total_rules': len(rule_engine.rules),
            'rules': rules_config,
            'categories': self.category_manager.categories
        }
    
    def get_classification_stats(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        获取分类统计信息
        
        Args:
            results: 分类结果列表
            
        Returns:
            统计信息
        """
        # 如果分类器有统计方法，直接使用
        if hasattr(self.classifier, 'get_classification_stats'):
            return self.classifier.get_classification_stats(results)
        
        # 否则自己计算统计信息
        stats = {
            'total_repos': len(results),
            'method': self.method,
            'categories': {},
            'confidence_distribution': {
                'high': 0,  # > 0.8
                'medium': 0,  # 0.5 - 0.8
                'low': 0  # < 0.5
            },
            'errors': 0
        }
        
        for result in results:
            classification = result.get('classification', {})
            
            # 统计分类类别
            categories = classification.get('categories', [])
            for category in categories:
                stats['categories'][category] = stats['categories'].get(category, 0) + 1
            
            # 统计置信度分布
            confidence = classification.get('confidence', 0)
            if confidence > 0.8:
                stats['confidence_distribution']['high'] += 1
            elif confidence >= 0.5:
                stats['confidence_distribution']['medium'] += 1
            else:
                stats['confidence_distribution']['low'] += 1
            
            # 统计错误
            if 'error' in classification:
                stats['errors'] += 1
        
        return stats
    
    def update_config(self, new_config: Dict[str, Any]):
        """
        更新配置并重新初始化分类器
        
        Args:
            new_config: 新配置
        """
        old_method = self.method
        self.config.update(new_config)
        
        # 获取新的分类方法
        classification_config = self.config.get('classification', {})
        self.method = classification_config.get('method', 'rules').lower()
        
        # 如果分类方法改变，重新创建分类器
        if self.method != old_method:
            logger.info(f"分类方法从 {old_method} 更改为 {self.method}，重新初始化分类器")
            self.classifier = self._create_classifier()
        
        logger.info("分类器配置更新完成")


def create_classifier_from_config(config_path: str) -> ProjectClassifier:
    """
    从配置文件创建分类器
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        项目分类器实例
    """
    import yaml
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        return ProjectClassifier(config)
        
    except Exception as e:
        logger.error(f"从配置文件 {config_path} 创建分类器失败: {e}")
        raise


def classify_repositories(repos: List[Dict[str, Any]], 
                         config: Dict[str, Any],
                         show_progress: bool = True) -> List[Dict[str, Any]]:
    """
    便捷函数：分类仓库列表
    
    Args:
        repos: 仓库列表
        config: 配置字典
        show_progress: 是否显示进度条
        
    Returns:
        分类结果列表
    """
    classifier = ProjectClassifier(config)
    return classifier.classify_batch(repos, show_progress)
