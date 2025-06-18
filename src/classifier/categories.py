"""
预定义分类体系

定义项目分类的层次结构和预设分类规则
"""

from typing import Dict, List, Set


class CategoryManager:
    """
    分类管理器
    
    管理项目分类的层次结构、分类定义和验证
    """
    
    def __init__(self):
        """初始化分类管理器"""
        self.categories = self._load_default_categories()
        self.tech_stack_keywords = self._load_tech_stack_keywords()
        self.purpose_keywords = self._load_purpose_keywords()
        self.language_mappings = self._load_language_mappings()
    
    def _load_default_categories(self) -> Dict[str, Dict[str, str]]:
        """
        加载默认分类体系
        
        Returns:
            分类体系字典
        """
        return {
            # 技术栈分类
            'tech_stack': {
                'web-frontend': 'Web前端开发',
                'web-backend': 'Web后端开发',
                'mobile': '移动应用开发',
                'desktop': '桌面应用开发',
                'game-dev': '游戏开发',
                'ai-ml': '人工智能与机器学习',
                'data-science': '数据科学',
                'devops': 'DevOps运维',
                'cloud': '云计算',
                'blockchain': '区块链',
                'iot': '物联网',
                'security': '网络安全',
                'testing': '软件测试',
                'documentation': '文档工具'
            },
            
            # 用途分类
            'purpose': {
                'framework': '开发框架',
                'library': '编程库',
                'tool': '开发工具',
                'application': '应用程序',
                'learning': '学习资源',
                'template': '项目模板',
                'example': '示例代码',
                'research': '研究项目',
                'automation': '自动化工具',
                'monitoring': '监控工具',
                'deployment': '部署工具'
            },
            
            # 编程语言分类
            'language': {
                'lang-python': 'Python',
                'lang-javascript': 'JavaScript',
                'lang-typescript': 'TypeScript',
                'lang-java': 'Java',
                'lang-go': 'Go',
                'lang-rust': 'Rust',
                'lang-cpp': 'C++',
                'lang-c': 'C',
                'lang-csharp': 'C#',
                'lang-php': 'PHP',
                'lang-ruby': 'Ruby',
                'lang-swift': 'Swift',
                'lang-kotlin': 'Kotlin',
                'lang-dart': 'Dart',
                'lang-r': 'R',
                'lang-matlab': 'MATLAB',
                'lang-shell': 'Shell',
                'lang-other': '其他语言'
            }
        }
    
    def _load_tech_stack_keywords(self) -> Dict[str, List[str]]:
        """
        加载技术栈关键词映射
        
        Returns:
            技术栈关键词字典
        """
        return {
            'web-frontend': [
                'react', 'vue', 'angular', 'svelte', 'html', 'css', 'javascript',
                'frontend', 'ui', 'ux', 'responsive', 'spa', 'pwa', 'webpack',
                'vite', 'parcel', 'sass', 'less', 'tailwind', 'bootstrap',
                'material-ui', 'antd', 'element-ui', 'nuxt', 'next', 'gatsby'
            ],
            'web-backend': [
                'express', 'koa', 'fastify', 'django', 'flask', 'fastapi',
                'spring', 'laravel', 'rails', 'gin', 'echo', 'actix',
                'backend', 'api', 'rest', 'graphql', 'microservice',
                'server', 'middleware', 'orm', 'database', 'auth'
            ],
            'mobile': [
                'react-native', 'flutter', 'ionic', 'cordova', 'phonegap',
                'xamarin', 'swift', 'kotlin', 'android', 'ios',
                'mobile', 'app', 'hybrid', 'native'
            ],
            'desktop': [
                'electron', 'tauri', 'qt', 'gtk', 'wpf', 'winforms',
                'javafx', 'swing', 'tkinter', 'pyqt', 'desktop',
                'gui', 'native', 'cross-platform'
            ],
            'game-dev': [
                'unity', 'unreal', 'godot', 'pygame', 'phaser',
                'game', 'gaming', '2d', '3d', 'engine', 'graphics'
            ],
            'ai-ml': [
                'tensorflow', 'pytorch', 'scikit-learn', 'keras',
                'machine-learning', 'deep-learning', 'neural-network',
                'ai', 'ml', 'nlp', 'computer-vision', 'reinforcement-learning'
            ],
            'data-science': [
                'pandas', 'numpy', 'matplotlib', 'seaborn', 'plotly',
                'jupyter', 'data-science', 'analytics', 'visualization',
                'statistics', 'data-mining', 'big-data'
            ],
            'devops': [
                'docker', 'kubernetes', 'terraform', 'ansible', 'jenkins',
                'gitlab-ci', 'github-actions', 'devops', 'ci-cd',
                'infrastructure', 'deployment', 'monitoring'
            ],
            'cloud': [
                'aws', 'azure', 'gcp', 'cloud', 'serverless', 'lambda',
                'functions', 'container', 'microservices'
            ],
            'blockchain': [
                'blockchain', 'ethereum', 'bitcoin', 'solidity', 'web3',
                'defi', 'nft', 'smart-contract', 'cryptocurrency'
            ],
            'iot': [
                'iot', 'arduino', 'raspberry-pi', 'embedded', 'sensor',
                'mqtt', 'internet-of-things'
            ],
            'security': [
                'security', 'cryptography', 'encryption', 'vulnerability',
                'penetration', 'cyber', 'auth', 'oauth', 'jwt'
            ],
            'testing': [
                'test', 'testing', 'unittest', 'jest', 'mocha', 'pytest',
                'selenium', 'cypress', 'automation', 'qa'
            ],
            'documentation': [
                'documentation', 'docs', 'wiki', 'markdown', 'sphinx',
                'gitbook', 'docusaurus', 'vuepress'
            ]
        }
    
    def _load_purpose_keywords(self) -> Dict[str, List[str]]:
        """
        加载用途关键词映射
        
        Returns:
            用途关键词字典
        """
        return {
            'framework': [
                'framework', 'platform', 'foundation', 'base', 'core'
            ],
            'library': [
                'library', 'lib', 'package', 'module', 'component',
                'utility', 'utils', 'helper'
            ],
            'tool': [
                'tool', 'cli', 'command', 'utility', 'generator',
                'builder', 'bundler', 'compiler'
            ],
            'application': [
                'app', 'application', 'software', 'program', 'client'
            ],
            'learning': [
                'tutorial', 'learning', 'course', 'education', 'guide',
                'example', 'demo', 'practice', 'exercise'
            ],
            'template': [
                'template', 'boilerplate', 'starter', 'scaffold',
                'skeleton', 'blueprint'
            ],
            'example': [
                'example', 'demo', 'sample', 'showcase', 'proof-of-concept'
            ],
            'research': [
                'research', 'paper', 'academic', 'experiment', 'study'
            ],
            'automation': [
                'automation', 'script', 'workflow', 'pipeline', 'bot'
            ],
            'monitoring': [
                'monitoring', 'metrics', 'logging', 'observability',
                'dashboard', 'alerting'
            ],
            'deployment': [
                'deploy', 'deployment', 'release', 'publish', 'distribution'
            ]
        }
    
    def _load_language_mappings(self) -> Dict[str, str]:
        """
        加载编程语言映射
        
        Returns:
            语言映射字典
        """
        return {
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
            'Shell': 'lang-shell',
            'Bash': 'lang-shell',
            'PowerShell': 'lang-shell'
        }
    
    def is_valid_category(self, category: str) -> bool:
        """
        检查分类是否有效
        
        Args:
            category: 分类名称
            
        Returns:
            是否有效
        """
        if category == 'uncategorized':
            return True
            
        for category_type, categories in self.categories.items():
            if category in categories:
                return True
        
        return False
    
    def get_all_categories(self) -> List[str]:
        """
        获取所有有效分类
        
        Returns:
            所有分类的列表
        """
        all_categories = []
        
        for category_type, categories in self.categories.items():
            all_categories.extend(categories.keys())
        
        # 添加特殊分类
        all_categories.append('uncategorized')
        
        return all_categories
    
    def get_category_display_name(self, category_id: str) -> str:
        """
        获取分类的显示名称
        
        Args:
            category_id: 分类标识
            
        Returns:
            分类显示名称
        """
        for category_type in self.categories.values():
            if category_id in category_type:
                return category_type[category_id]
        return category_id
    
    def get_categories_by_type(self, category_type: str) -> Dict[str, str]:
        """
        根据类型获取分类
        
        Args:
            category_type: 分类类型 (tech_stack, purpose, language)
            
        Returns:
            该类型的分类字典
        """
        return self.categories.get(category_type, {})
    
    def validate_categories(self, categories: List[str]) -> List[str]:
        """
        验证分类是否有效
        
        Args:
            categories: 待验证的分类列表
            
        Returns:
            有效的分类列表
        """
        valid_categories = self.get_all_categories()
        return [cat for cat in categories if cat in valid_categories or cat == 'uncategorized']
    
    def get_language_category(self, language: str) -> str:
        """
        根据编程语言获取分类
        
        Args:
            language: 编程语言名称
            
        Returns:
            语言分类标识
        """
        return self.language_mappings.get(language, 'lang-other')
    
    def search_categories_by_keywords(self, text: str) -> Set[str]:
        """
        根据关键词搜索相关分类
        
        Args:
            text: 搜索文本
            
        Returns:
            匹配的分类集合
        """
        if not text:
            return set()
        
        text_lower = text.lower()
        matched_categories = set()
        
        # 搜索技术栈关键词
        for category, keywords in self.tech_stack_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    matched_categories.add(category)
        
        # 搜索用途关键词
        for category, keywords in self.purpose_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    matched_categories.add(category)
        
        return matched_categories
    
    def get_category_statistics(self, classified_repos: List[Dict]) -> Dict[str, int]:
        """
        获取分类统计信息
        
        Args:
            classified_repos: 已分类的项目列表
            
        Returns:
            分类统计字典
        """
        stats = {}
        
        for repo in classified_repos:
            categories = repo.get('categories', [])
            for category in categories:
                stats[category] = stats.get(category, 0) + 1
        
        return dict(sorted(stats.items(), key=lambda x: x[1], reverse=True))
    
    def organize_by_categories(self, classified_repos: List[Dict]) -> Dict[str, List[Dict]]:
        """
        按分类组织项目
        
        Args:
            classified_repos: 已分类的项目列表
            
        Returns:
            按分类组织的项目字典
        """
        organized = {}
        
        for repo in classified_repos:
            categories = repo.get('categories', ['uncategorized'])
            
            for category in categories:
                if category not in organized:
                    organized[category] = []
                organized[category].append(repo)
        
        return organized
