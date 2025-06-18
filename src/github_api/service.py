"""
GitHub服务管理器

整合GitHub API客户端、获取器和缓存管理器，提供统一的高级接口
"""

import logging
from typing import List, Dict, Any, Optional

from src.config.settings import Config
from src.config.auth import GitHubAuth
from src.utils.cache import CacheManager
from .client import GitHubClient
from .fetcher import StarredFetcher


logger = logging.getLogger(__name__)


class GitHubService:
    """
    GitHub服务管理器
    
    提供GitHub API的统一高级接口，整合客户端、获取器和缓存管理
    """
    
    def __init__(self, config: Config):
        """
        初始化GitHub服务
        
        Args:
            config: 项目配置对象
        """
        self.config = config
        
        # 初始化认证
        self.auth = GitHubAuth(config)
        
        # 初始化GitHub客户端
        self.client = GitHubClient(self.auth)
        
        # 初始化获取器
        self.fetcher = StarredFetcher(self.client)
        
        # 初始化缓存管理器（如果启用）
        cache_config = config.get_cache_manager_config()
        self.cache_manager = None
        if cache_config.get('enabled', True):
            self.cache_manager = CacheManager(
                cache_dir=cache_config.get('cache_dir', '.cache'),
                cache_format=cache_config.get('format', 'json')
            )
        
        self.username = None
        logger.info("GitHub服务初始化完成")
    
    def test_connection(self) -> bool:
        """
        测试GitHub连接
        
        Returns:
            连接是否成功
        """
        return self.client.test_connection()
    
    def get_authenticated_user(self):
        """
        获取认证用户信息
        
        Returns:
            用户信息
        """
        if not self.username:
            user = self.client.get_authenticated_user()
            self.username = user.login
            logger.info(f"已认证用户: {self.username}")
        
        return self.username
    
    def fetch_starred_repos(self, use_cache: bool = True, 
                           force_refresh: bool = False,
                           show_progress: bool = True) -> List[Dict[str, Any]]:
        """
        获取星标项目
        
        Args:
            use_cache: 是否使用缓存
            force_refresh: 是否强制刷新（忽略缓存）
            show_progress: 是否显示进度条
            
        Returns:
            星标项目数据列表
        """
        # 获取用户名
        username = self.get_authenticated_user()
        
        # 检查缓存
        cache_valid = False
        cached_repos = None
        
        if use_cache and self.cache_manager and not force_refresh:
            cache_config = self.config.get_cache_manager_config()
            cache_valid = self.cache_manager.is_user_cache_valid(
                username, 
                cache_config.get('ttl_hours', 24)
            )
            
            if cache_valid:
                cached_repos = self.cache_manager.load_starred_repos(username)
                if cached_repos:
                    logger.info(f"从缓存加载 {len(cached_repos)} 个星标项目")
                    return cached_repos
        
        # 从API获取数据
        logger.info("从GitHub API获取星标项目...")
        repos = self.fetcher.fetch_all_starred(show_progress=show_progress)
        
        # 保存到缓存
        if use_cache and self.cache_manager and repos:
            metadata = {
                'username': username,
                'fetch_method': 'api',
                'total_count': len(repos)
            }
            
            success = self.cache_manager.save_starred_repos(
                username, 
                repos, 
                metadata
            )
            
            if success:
                logger.info(f"已缓存 {len(repos)} 个星标项目")
        
        return repos
    
    def get_starred_summary(self) -> Dict[str, Any]:
        """
        获取星标项目摘要
        
        Returns:
            摘要信息
        """
        username = self.get_authenticated_user()
        summary = self.fetcher.get_starred_summary()
        
        # 添加缓存信息
        if self.cache_manager:
            cache_info = self.cache_manager.cache.get_cache_info(
                self.cache_manager.get_user_cache_key(username)
            )
            summary['cache_info'] = cache_info
        
        return summary
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """
        获取API速率限制状态
        
        Returns:
            速率限制状态
        """
        return self.client.get_rate_limit_status()
    
    def clear_cache(self, username: Optional[str] = None) -> bool:
        """
        清理缓存
        
        Args:
            username: 指定用户名，如果为None则清理当前用户缓存
            
        Returns:
            是否清理成功
        """
        if not self.cache_manager:
            logger.warning("缓存管理器未启用")
            return False
        
        if not username:
            username = self.get_authenticated_user()
        
        cache_key = self.cache_manager.get_user_cache_key(username)
        return self.cache_manager.cache.clear_cache(cache_key)
    
    def cleanup_expired_cache(self) -> int:
        """
        清理过期缓存
        
        Returns:
            清理的文件数量
        """
        if not self.cache_manager:
            return 0
        
        cache_config = self.config.get_cache_manager_config()
        max_age_hours = cache_config.get('max_age_hours', 168)  # 默认7天
        
        return self.cache_manager.cache.cleanup_expired_cache(max_age_hours)
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        获取缓存信息
        
        Returns:
            缓存信息字典
        """
        if not self.cache_manager:
            return {'enabled': False}
        
        username = self.get_authenticated_user()
        cache_info = self.cache_manager.cache.get_cache_info(
            self.cache_manager.get_user_cache_key(username)
        )
        
        # 添加全局缓存统计
        all_cache_files = self.cache_manager.cache.list_cache_files()
        cache_info.update({
            'enabled': True,
            'total_cache_files': len(all_cache_files),
            'cache_directory': str(self.cache_manager.cache.cache_dir)
        })
        
        return cache_info
    
    def validate_config(self) -> Dict[str, Any]:
        """
        验证配置和连接
        
        Returns:
            验证结果
        """
        result = {
            'config_valid': False,
            'connection_valid': False,
            'cache_enabled': False,
            'errors': [],
            'warnings': []
        }
        
        try:
            # 验证基本配置
            result['config_valid'] = self.config.validate()
            
            # 测试连接
            result['connection_valid'] = self.test_connection()
            
            # 检查缓存
            result['cache_enabled'] = self.cache_manager is not None
            
            # 检查API限制
            rate_limit = self.get_rate_limit_status()
            core_remaining = rate_limit.get('core', {}).get('remaining', 0)
            
            if core_remaining < 100:
                result['warnings'].append(f"API请求配额较低: {core_remaining} 次剩余")
            
            # 获取用户信息
            if result['connection_valid']:
                username = self.get_authenticated_user()
                result['username'] = username
            
        except Exception as e:
            result['errors'].append(f"验证过程中出错: {str(e)}")
            logger.error(f"配置验证失败: {e}")
        
        return result


def create_github_service(config: Optional[Config] = None) -> GitHubService:
    """
    创建GitHub服务实例的便捷函数
    
    Args:
        config: 配置对象，如果为None则使用默认配置
        
    Returns:
        GitHub服务实例
    """
    if config is None:
        config = Config()
    
    return GitHubService(config)
