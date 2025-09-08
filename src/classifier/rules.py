"""
分类规则引擎

基于规则的项目分类系统，支持可配置的分类规则和扩展
"""

import re
import logging
from typing import Dict, List, Callable, Any, Optional
from .categories import CategoryManager


logger = logging.getLogger(__name__)


class ClassificationRule:
    """
    分类规则类
    
    定义单个分类规则的结构和匹配逻辑
    """
    
    def __init__(self, name: str, condition: Callable[[Dict], bool], 
                 category: str, priority: int = 0, description: str = ""):
        """
        初始化分类规则
        
        Args:
            name: 规则名称
            condition: 匹配条件函数
            category: 目标分类
            priority: 优先级（数字越大优先级越高）
            description: 规则描述
        """
        self.name = name
        self.condition = condition
        self.category = category
        self.priority = priority
        self.description = description
    
    def matches(self, repo_data: Dict[str, Any]) -> bool:
        """
        检查仓库数据是否匹配此规则
        
        Args:
            repo_data: 仓库数据字典
            
        Returns:
            是否匹配
        """
        try:
            return self.condition(repo_data)
        except Exception as e:
            logger.warning(f"规则 {self.name} 匹配时出错: {e}")
            return False
    
    def __repr__(self) -> str:
        return f"ClassificationRule(name='{self.name}', category='{self.category}', priority={self.priority})"


class RuleEngine:
    """
    分类规则引擎
    
    管理和执行所有分类规则
    """
    
    def __init__(self, category_manager: Optional[CategoryManager] = None):
        """
        初始化规则引擎
        
        Args:
            category_manager: 分类管理器
        """
        self.rules: List[ClassificationRule] = []
        self.category_manager = category_manager or CategoryManager()
        self._setup_default_rules()
    
    def add_rule(self, rule: ClassificationRule) -> None:
        """
        添加分类规则
        
        Args:
            rule: 分类规则
        """
        self.rules.append(rule)
        # 按优先级排序
        self.rules.sort(key=lambda r: r.priority, reverse=True)
        logger.debug(f"添加规则: {rule.name}")
    
    def remove_rule(self, rule_name: str) -> bool:
        """
        移除分类规则
        
        Args:
            rule_name: 规则名称
            
        Returns:
            是否成功移除
        """
        original_count = len(self.rules)
        self.rules = [r for r in self.rules if r.name != rule_name]
        removed = len(self.rules) < original_count
        
        if removed:
            logger.debug(f"移除规则: {rule_name}")
        
        return removed
    
    def classify(self, repo_data: Dict[str, Any]) -> List[str]:
        """
        对仓库进行分类
        
        Args:
            repo_data: 仓库数据字典
            
        Returns:
            分类列表
        """
        matched_categories = []
        
        for rule in self.rules:
            if rule.matches(repo_data):
                if rule.category not in matched_categories:
                    matched_categories.append(rule.category)
                    logger.debug(f"仓库 {repo_data.get('full_name', 'Unknown')} 匹配规则: {rule.name} -> {rule.category}")
        
        # 如果没有匹配任何规则，返回uncategorized
        if not matched_categories:
            matched_categories = ['uncategorized']
        
        return matched_categories
    
    def classify_with_details(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        对仓库进行分类并返回详细信息
        
        Args:
            repo_data: 仓库数据字典
            
        Returns:
            分类结果详情
        """
        matched_rules = []
        matched_categories = []
        
        for rule in self.rules:
            if rule.matches(repo_data):
                matched_rules.append({
                    'name': rule.name,
                    'category': rule.category,
                    'priority': rule.priority,
                    'description': rule.description
                })
                if rule.category not in matched_categories:
                    matched_categories.append(rule.category)
        
        if not matched_categories:
            matched_categories = ['uncategorized']
        
        return {
            'categories': matched_categories,
            'matched_rules': matched_rules,
            'method': 'rules',
            'confidence': 0.8 if matched_categories != ['uncategorized'] else 0.1,
            'reasoning': f"匹配了 {len(matched_rules)} 个规则" if matched_rules else "未匹配任何规则"
        }
    
    def setup_default_rules(self) -> None:
        """
        设置默认分类规则（公有方法）
        
        清除现有规则并重新加载默认规则
        """
        self.rules.clear()
        self._setup_default_rules()
        logger.info(f"已重新加载 {len(self.rules)} 条默认分类规则")
    
    def _setup_default_rules(self) -> None:
        """设置默认分类规则"""
        
        # 编程语言规则
        self._add_language_rules()
        
        # 技术栈规则
        self._add_tech_stack_rules()
        
        # 用途规则
        self._add_purpose_rules()
        
        # 特殊项目规则
        self._add_special_rules()
    
    def _add_language_rules(self) -> None:
        """添加编程语言分类规则"""
        
        def create_language_rule(language: str, category: str) -> ClassificationRule:
            return ClassificationRule(
                name=f"language_{language.lower()}",
                condition=lambda repo: repo.get('language', '').lower() == language.lower(),
                category=category,
                priority=10,
                description=f"基于编程语言 {language} 的分类"
            )
        
        # 主要编程语言
        languages = {
            'Python': 'lang-python',
            'JavaScript': 'lang-javascript',
            'TypeScript': 'lang-typescript',
            'Java': 'lang-java',
            'Go': 'lang-go',
            'Rust': 'lang-rust',
            'C++': 'lang-cpp',
            'C': 'lang-c',
            'C#': 'lang-csharp',
            'PHP': 'lang-php',
            'Ruby': 'lang-ruby',
            'Swift': 'lang-swift',
            'Kotlin': 'lang-kotlin',
            'Dart': 'lang-dart',
            'R': 'lang-r',
            'MATLAB': 'lang-matlab',
            'Shell': 'lang-shell'
        }
        
        for language, category in languages.items():
            self.add_rule(create_language_rule(language, category))
    
    def _add_tech_stack_rules(self) -> None:
        """添加技术栈分类规则"""
        
        tech_keywords = self.category_manager.tech_stack_keywords
        
        for category, keywords in tech_keywords.items():
            self.add_rule(ClassificationRule(
                name=f"tech_stack_{category}",
                condition=lambda repo, kw=keywords: self._has_keywords(repo, kw) or self._has_topics(repo, kw),
                category=category,
                priority=20,
                description=f"基于 {category} 技术栈的分类"
            ))

    def _add_purpose_rules(self) -> None:
        """添加用途分类规则"""
        
        purpose_keywords = self.category_manager.purpose_keywords

        for category, keywords in purpose_keywords.items():
            self.add_rule(ClassificationRule(
                name=f"purpose_{category}",
                condition=lambda repo, kw=keywords: self._has_keywords(repo, kw) or self._has_topics(repo, kw),
                category=category,
                priority=15,
                description=f"基于 {category} 用途的分类"
            ))
    
    def _add_special_rules(self) -> None:
        """添加特殊项目规则"""
        
        # 分叉项目标识
        self.add_rule(ClassificationRule(
            name="fork_identification",
            condition=lambda repo: repo.get('fork', False),
            category="fork",
            priority=5,
            description="识别分叉项目"
        ))
        
        # 归档项目标识
        self.add_rule(ClassificationRule(
            name="archived_identification",
            condition=lambda repo: repo.get('archived', False),
            category="archived",
            priority=5,
            description="识别归档项目"
        ))
        
        # 高星标项目（移除无效分类，改为其他用途分类）
        # self.add_rule(ClassificationRule(
        #     name="popular_project",
        #     condition=lambda repo: repo.get('stargazers_count', 0) >= 1000,
        #     category="popular",  # 这是一个无效分类
        #     priority=5,
        #     description="识别高星标项目（1000+）"
        # ))
    
    def _has_keywords(self, repo_data: Dict[str, Any], keywords: List[str]) -> bool:
        """
        检查仓库是否包含指定关键词
        
        Args:
            repo_data: 仓库数据
            keywords: 关键词列表
            
        Returns:
            是否包含关键词
        """
        search_text = (
            (repo_data.get('name', '') + ' ' +
             repo_data.get('description', '') + ' ' +
             repo_data.get('full_name', '')).lower()
        )
        
        return any(keyword.lower() in search_text for keyword in keywords)
    
    def _has_topics(self, repo_data: Dict[str, Any], topics: List[str]) -> bool:
        """
        检查仓库是否包含指定主题
        
        Args:
            repo_data: 仓库数据
            topics: 主题列表
            
        Returns:
            是否包含主题
        """
        repo_topics = [topic.lower() for topic in repo_data.get('topics', [])]
        return any(topic.lower() in repo_topics for topic in topics)
    
    def get_rules_summary(self) -> Dict[str, Any]:
        """
        获取规则摘要信息
        
        Returns:
            规则摘要字典
        """
        return {
            'total_rules': len(self.rules),
            'categories_covered': len(set(rule.category for rule in self.rules)),
            'rules_by_category': {
                category: len([r for r in self.rules if r.category == category])
                for category in set(rule.category for rule in self.rules)
            },
            'rules_by_priority': {
                str(priority): len([r for r in self.rules if r.priority == priority])
                for priority in set(rule.priority for rule in self.rules)
            }
        }


class RuleBasedClassifier:
    """
    基于规则的分类器
    
    使用规则引擎进行项目分类
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化基于规则的分类器
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.category_manager = CategoryManager()
        self.rule_engine = RuleEngine(self.category_manager)
        
        logger.info("基于规则的分类器初始化完成")
    
    def classify_repo(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分类单个仓库
        
        Args:
            repo_data: 仓库数据字典
            
        Returns:
            分类结果字典
        """
        result = self.rule_engine.classify_with_details(repo_data)
        
        # 添加语言分类
        language = repo_data.get('language')
        if language:
            language_category = self.category_manager.get_language_category(language)
            if language_category not in result['categories']:
                result['categories'].append(language_category)
        
        # 验证分类有效性
        result['categories'] = self.category_manager.validate_categories(result['categories'])
        
        return result
    
    def classify_batch(self, repos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        批量分类仓库
        
        Args:
            repos: 仓库数据列表
            
        Returns:
            分类结果列表
        """
        results = []
        
        try:
            from tqdm import tqdm
            repos_iter = tqdm(repos, desc="规则分类项目")
        except ImportError:
            repos_iter = repos
        
        for repo in repos_iter:
            try:
                result = self.classify_repo(repo)
                # 将分类结果合并到原始数据
                repo_with_classification = repo.copy()
                repo_with_classification.update(result)
                results.append(repo_with_classification)
            except Exception as e:
                logger.error(f"分类项目 {repo.get('full_name', 'Unknown')} 失败: {e}")
                # 添加错误信息
                repo_with_error = repo.copy()
                repo_with_error.update({
                    'categories': ['uncategorized'],
                    'error': str(e),
                    'method': 'rules',
                    'confidence': 0.0
                })
                results.append(repo_with_error)
        
        return results
    
    def get_classification_stats(self, classified_repos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        获取分类统计信息
        
        Args:
            classified_repos: 已分类的仓库列表
            
        Returns:
            统计信息字典
        """
        category_stats = self.category_manager.get_category_statistics(classified_repos)
        
        return {
            'total_repos': len(classified_repos),
            'total_categories': len(category_stats),
            'category_distribution': category_stats,
            'uncategorized_count': category_stats.get('uncategorized', 0),
            'categorized_count': len(classified_repos) - category_stats.get('uncategorized', 0)
        }
