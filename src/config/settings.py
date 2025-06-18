"""
项目配置管理模块

负责加载和管理项目配置，包括环境变量和YAML配置文件。
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv


class Config:
    """项目配置管理类"""
    
    def __init__(self, config_file: str = 'config.yaml'):
        """
        初始化配置管理
        
        Args:
            config_file: 配置文件路径，默认为config.yaml
        """
        self.config_file = config_file
        self.config: Dict[str, Any] = {}
        
        # 加载.env文件（如果存在）
        load_dotenv()
        
        # 加载配置文件
        self.load_config(config_file)
        
    def load_config(self, file_path: str) -> None:
        """
        加载YAML配置文件
        
        Args:
            file_path: 配置文件路径
        """
        config_path = Path(file_path)
        
        if not config_path.exists():
            # 如果配置文件不存在，创建默认配置
            self.config = self._get_default_config()
            self.save_config(file_path)
            print(f"配置文件 {file_path} 不存在，已创建默认配置")
        else:
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.config = yaml.safe_load(f) or {}
                print(f"成功加载配置文件: {file_path}")
            except Exception as e:
                print(f"加载配置文件失败: {e}")
                self.config = self._get_default_config()
    
    def save_config(self, file_path: str) -> None:
        """
        保存配置到YAML文件
        
        Args:
            file_path: 配置文件路径
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, 
                         allow_unicode=True, indent=2)
            print(f"配置已保存到: {file_path}")
        except Exception as e:
            print(f"保存配置文件失败: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值，支持点分隔的嵌套键
        
        Args:
            key: 配置键，支持'github.token_env'格式
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
                
        return value
    
    def get_env(self, env_name: str, default: Optional[str] = None) -> Optional[str]:
        """
        获取环境变量
        
        Args:
            env_name: 环境变量名
            default: 默认值
            
        Returns:
            环境变量值
        """
        return os.getenv(env_name, default)
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        获取默认配置
        
        Returns:
            默认配置字典
        """
        return {
            'github': {
                'token_env': 'GITHUB_TOKEN',
                'username': '',
                'api_base_url': 'https://api.github.com',
                'timeout': 30,
                'retry_count': 3,
                'retry_delay': 1,
                'per_page': 100,
                'rate_limit': {
                    'check_threshold': 100,
                    'check_interval': 300,
                    'wait_on_limit': True,
                    'max_wait_time': 3600
                }
            },
            'fetcher': {
                'batch_size': 100,
                'show_progress': True,
                'include_forks': True,
                'include_archived': True,
                'max_repos': None,
                'fields': [
                    'id', 'name', 'full_name', 'description', 'html_url',
                    'clone_url', 'ssh_url', 'homepage', 'private', 'fork',
                    'archived', 'disabled', 'stargazers_count', 'watchers_count',
                    'forks_count', 'open_issues_count', 'size', 'language',
                    'topics', 'created_at', 'updated_at', 'pushed_at',
                    'license', 'owner'
                ]
            },
            'classification': {
                'method': 'hybrid',  # rules, ai, hybrid
            },
            'ai_classification': {
                'enabled': True,
                'api_key_env': 'OPENAI_API_KEY',
                'model': 'gpt-3.5-turbo',
                'always_use': False,
                'fallback_to_rules': True,
                'batch_size': 5,
                'max_retries': 3
            },
            'output': {
                'format': 'markdown',
                'template': 'templates/default.md',
                'output_dir': 'output',
                'filename': 'starred-projects.md'
            },
            'cache': {
                'enabled': True,
                'ttl_hours': 24,
                'cache_dir': '.cache',
                'format': 'json',
                'auto_cleanup': True,
                'max_age_hours': 168  # 7 days
            },
            'logging': {
                'level': 'INFO',
                'file': 'star_summary.log',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'max_size_mb': 10,
                'backup_count': 3
            }
        }
    
    @property
    def github_token(self) -> Optional[str]:
        """
        获取GitHub Token
        
        Returns:
            GitHub Token或None
        """
        token_env = self.get('github.token_env', 'GITHUB_TOKEN')
        return self.get_env(token_env)
    
    @property
    def openai_api_key(self) -> Optional[str]:
        """
        获取OpenAI API Key
        
        Returns:
            OpenAI API Key或None
        """
        key_env = self.get('ai_classification.api_key_env', 'OPENAI_API_KEY')
        return self.get_env(key_env)
    
    @property
    def github_config(self) -> Dict[str, Any]:
        """
        获取GitHub配置
        
        Returns:
            GitHub配置字典
        """
        return self.get('github', {})
    
    @property
    def fetcher_config(self) -> Dict[str, Any]:
        """
        获取数据获取器配置
        
        Returns:
            获取器配置字典
        """
        return self.get('fetcher', {})
    
    @property
    def cache_config(self) -> Dict[str, Any]:
        """
        获取缓存配置
        
        Returns:
            缓存配置字典
        """
        return self.get('cache', {})
    
    def get_github_client_config(self) -> Dict[str, Any]:
        """
        获取GitHub客户端配置
        
        Returns:
            客户端配置字典
        """
        github_config = self.github_config
        return {
            'token': self.github_token,
            'base_url': github_config.get('api_base_url', 'https://api.github.com'),
            'timeout': github_config.get('timeout', 30),
            'retry': {
                'count': github_config.get('retry_count', 3),
                'delay': github_config.get('retry_delay', 1)
            },
            'per_page': github_config.get('per_page', 100),
            'rate_limit': github_config.get('rate_limit', {})
        }
    
    def get_cache_manager_config(self) -> Dict[str, Any]:
        """
        获取缓存管理器配置
        
        Returns:
            缓存管理器配置字典
        """
        cache_config = self.cache_config
        return {
            'enabled': cache_config.get('enabled', True),
            'cache_dir': cache_config.get('cache_dir', '.cache'),
            'format': cache_config.get('format', 'json'),
            'ttl_hours': cache_config.get('ttl_hours', 24),
            'auto_cleanup': cache_config.get('auto_cleanup', True),
            'max_age_hours': cache_config.get('max_age_hours', 168)
        }
    
    def validate(self) -> bool:
        """
        验证配置的有效性
        
        Returns:
            配置是否有效
        """
        # 检查必需的GitHub Token
        if not self.github_token:
            print("错误: 未找到GitHub Token，请设置环境变量")
            return False
        
        # 检查AI分类配置（如果启用）
        if self.get('ai_classification.enabled', False):
            if not self.openai_api_key:
                print("警告: AI分类已启用但未找到OpenAI API Key")
        
        return True
    
    def get_output_config(self):
        """获取输出配置"""
        output_config = self.config.get('output', {})
        
        # 默认配置
        defaults = {
            'format': 'markdown',
            'base_dir': 'output',
            'markdown': {
                'filename': 'README.md',  # 默认改为README.md
                'template': 'templates/main.md',
                'include_toc': True
            },
            'json': {
                'filename': 'starred-projects.json',
                'pretty_print': True
            },
            'paths': {
                'main_readme': 'README.md',
                'docs_readme': 'docs/README.md',
                'categories_dir': 'output/categories',
                'raw_data': 'output/raw/starred-repos.json'
            }
        }
        
        # 合并配置
        for key, default_value in defaults.items():
            if key not in output_config:
                output_config[key] = default_value
            elif isinstance(default_value, dict):
                for sub_key, sub_default in default_value.items():
                    if sub_key not in output_config[key]:
                        output_config[key][sub_key] = sub_default
        
        return output_config
    
    def get_output_path(self, path_type='main_readme'):
        """获取输出文件路径
        
        Args:
            path_type: 路径类型，可选值：
                - 'main_readme': 主README文件
                - 'docs_readme': 文档README文件  
                - 'categories_dir': 分类目录
                - 'raw_data': 原始数据文件
                - 'markdown': 默认Markdown文件
                - 'json': JSON数据文件
        """
        output_config = self.get_output_config()
        
        if path_type in ['markdown', 'json']:
            # 获取格式化文件路径
            base_dir = output_config.get('base_dir', 'output')
            filename = output_config.get(path_type, {}).get('filename')
            if filename:
                return os.path.join(base_dir, filename)
        
        # 获取预定义路径
        paths = output_config.get('paths', {})
        if path_type in paths:
            path = paths[path_type]
            if path:  # 确保路径不为空
                # 如果是相对路径，确保目录存在
                if not os.path.isabs(path) and os.path.dirname(path):
                    os.makedirs(os.path.dirname(path), exist_ok=True)
                return path
        
        # 默认返回主README路径
        return output_config.get('paths', {}).get('main_readme', 'README.md')
