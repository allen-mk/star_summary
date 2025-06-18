"""
混合分类器

结合规则分类和AI分类的混合分类系统
"""

import logging
from typing import Dict, List, Any, Optional

from .rules import RuleEngine
from .categories import CategoryManager
from .ai_classifier import AIClassifier


logger = logging.getLogger(__name__)


class HybridClassifier:
    """
    混合分类器
    
    结合规则分类和AI分类，提供更准确和灵活的分类能力
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化混合分类器
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.rule_engine = RuleEngine()
        self.category_manager = CategoryManager()
        self.ai_classifier = None
        
        # 初始化AI分类器（如果配置了）
        ai_config = config.get('ai_classification', {})
        if ai_config.get('enabled', False):
            api_key = self._get_api_key(ai_config)
            model = ai_config.get('model', 'gpt-3.5-turbo')
            
            if api_key:
                try:
                    self.ai_classifier = AIClassifier(
                        api_key=api_key,
                        model=model,
                        category_manager=self.category_manager
                    )
                    logger.info("AI分类器初始化成功")
                except Exception as e:
                    logger.error(f"AI分类器初始化失败: {e}")
                    if not ai_config.get('fallback_to_rules', True):
                        raise
            else:
                logger.warning("未找到AI API密钥，将仅使用规则分类")
        
        # 设置默认规则
        self.setup_default_rules()
    
    def _get_api_key(self, ai_config: Dict[str, Any]) -> Optional[str]:
        """
        获取API密钥
        
        Args:
            ai_config: AI配置
            
        Returns:
            API密钥
        """
        import os
        
        # 从配置中直接获取
        if 'api_key' in ai_config:
            return ai_config['api_key']
        
        # 从环境变量获取
        env_var = ai_config.get('api_key_env', 'OPENAI_API_KEY')
        return os.getenv(env_var)
    
    def setup_default_rules(self):
        """设置默认分类规则"""
        self.rule_engine.setup_default_rules()
        logger.info(f"已加载 {len(self.rule_engine.rules)} 条分类规则")
    
    def classify_repo(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分类单个项目
        
        Args:
            repo_data: 项目数据
            
        Returns:
            分类结果
        """
        # 首先使用规则分类
        rule_categories = self.rule_engine.classify(repo_data)
        
        result = {
            "categories": rule_categories,
            "method": "rules",
            "confidence": 0.8,
            "reasoning": "基于预定义规则分类",
            "rule_categories": rule_categories
        }
        
        # 判断是否需要使用AI分类
        should_use_ai = self._should_use_ai_classification(rule_categories)
        
        if should_use_ai and self.ai_classifier:
            try:
                ai_result = self.ai_classifier.classify_repo(repo_data)
                
                # 合并分类结果
                if ai_result.get('confidence', 0) > 0.7:
                    combined_categories = self._merge_categories(
                        rule_categories, 
                        ai_result.get('categories', [])
                    )
                    
                    result.update({
                        "categories": combined_categories,
                        "method": "hybrid",
                        "confidence": max(0.8, ai_result.get('confidence', 0)),
                        "ai_confidence": ai_result.get('confidence', 0),
                        "ai_categories": ai_result.get('categories', []),
                        "ai_reasoning": ai_result.get('reasoning', ""),
                        "reasoning": f"规则分类: {rule_categories}, AI增强: {ai_result.get('categories', [])}"
                    })
                    
                    logger.debug(f"混合分类完成: {repo_data.get('name', 'Unknown')} -> {combined_categories}")
                else:
                    logger.debug(f"AI分类置信度过低({ai_result.get('confidence', 0):.2f})，使用规则分类结果")
                    
            except Exception as e:
                logger.error(f"AI分类失败: {e}")
                result["ai_error"] = str(e)
                
                # 如果配置不允许回退到规则分类，则抛出异常
                if not self.config.get('ai_classification', {}).get('fallback_to_rules', True):
                    raise
        
        return result
    
    def _should_use_ai_classification(self, rule_categories: List[str]) -> bool:
        """
        判断是否应该使用AI分类
        
        Args:
            rule_categories: 规则分类结果
            
        Returns:
            是否使用AI分类
        """
        ai_config = self.config.get('ai_classification', {})
        
        # 如果配置总是使用AI
        if ai_config.get('always_use', False):
            return True
        
        # 如果规则分类结果不理想（只有uncategorized或为空）
        if (not rule_categories or 
            (len(rule_categories) == 1 and rule_categories[0] == 'uncategorized')):
            return True
        
        # 如果规则分类结果过少
        if len(rule_categories) < ai_config.get('min_categories_threshold', 2):
            return True
        
        return False
    
    def _merge_categories(self, rule_categories: List[str], 
                         ai_categories: List[str]) -> List[str]:
        """
        合并规则分类和AI分类结果
        
        Args:
            rule_categories: 规则分类结果
            ai_categories: AI分类结果
            
        Returns:
            合并后的分类结果
        """
        # 合并所有分类，去重
        all_categories = list(set(rule_categories + ai_categories))
        
        # 如果有其他有效分类，移除uncategorized
        if len(all_categories) > 1 and 'uncategorized' in all_categories:
            all_categories.remove('uncategorized')
        
        # 验证分类的有效性
        valid_categories = []
        for category in all_categories:
            if self.category_manager.is_valid_category(category):
                valid_categories.append(category)
            else:
                logger.warning(f"无效分类被过滤: {category}")
        
        return valid_categories or ['uncategorized']
    
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
        results = []
        
        if show_progress:
            try:
                from tqdm import tqdm
                iterator = tqdm(repos, desc="混合分类项目", unit="项目")
            except ImportError:
                logger.warning("未安装tqdm，将不显示进度条")
                iterator = repos
        else:
            iterator = repos
        
        for repo in iterator:
            try:
                result = self.classify_repo(repo)
                results.append({
                    'repo': repo,
                    'classification': result
                })
            except Exception as e:
                logger.error(f"分类项目 {repo.get('name', 'Unknown')} 时出错: {e}")
                results.append({
                    'repo': repo,
                    'classification': {
                        'categories': ['uncategorized'],
                        'method': 'error',
                        'confidence': 0.0,
                        'reasoning': f"分类出错: {str(e)}",
                        'error': str(e)
                    }
                })
        
        return results
    
    def get_classification_stats(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        获取分类统计信息
        
        Args:
            results: 分类结果列表
            
        Returns:
            统计信息
        """
        stats = {
            'total_repos': len(results),
            'methods': {},
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
            
            # 统计分类方法
            method = classification.get('method', 'unknown')
            stats['methods'][method] = stats['methods'].get(method, 0) + 1
            
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
