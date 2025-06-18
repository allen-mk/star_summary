"""
GitHub API 客户端封装

提供对PyGithub库的高级封装，包括速率限制处理、错误处理和连接管理。
"""

import time
import logging
from typing import Optional, Dict, Any
from functools import wraps
from github import Github, RateLimitExceededException
from github.Repository import Repository
from github.PaginatedList import PaginatedList

from src.config.auth import GitHubAuth


logger = logging.getLogger(__name__)


def handle_rate_limit(func):
    """
    装饰器：处理GitHub API速率限制
    
    当遇到速率限制时，计算等待时间并自动重试
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                return func(*args, **kwargs)
            except RateLimitExceededException as e:
                retry_count += 1
                if retry_count >= max_retries:
                    logger.error(f"达到最大重试次数，放弃请求: {e}")
                    raise
                
                # 计算等待时间
                wait_time = calculate_wait_time(e)
                logger.warning(f"遇到速率限制，等待 {wait_time} 秒后重试 (第{retry_count}次重试)")
                time.sleep(wait_time)
            except Exception as e:
                logger.error(f"API请求失败: {e}")
                raise
        
        return None
    return wrapper


def calculate_wait_time(exception: RateLimitExceededException) -> int:
    """
    计算速率限制等待时间
    
    Args:
        exception: 速率限制异常
        
    Returns:
        等待时间（秒）
    """
    # 如果异常中包含重置时间，计算到重置时间的等待时间
    # 否则使用默认等待时间
    try:
        # 获取速率限制重置时间（通常是Unix时间戳）
        reset_time = getattr(exception, 'reset_time', None)
        if reset_time:
            current_time = int(time.time())
            wait_time = max(reset_time - current_time + 10, 60)  # 额外等待10秒
            return min(wait_time, 3600)  # 最多等待1小时
    except:
        pass
    
    # 默认等待时间
    return 60


class RateLimitHandler:
    """
    GitHub API速率限制管理器
    """
    
    def __init__(self, github_client: Github):
        """
        初始化速率限制管理器
        
        Args:
            github_client: GitHub客户端实例
        """
        self.client = github_client
        self.last_check_time = 0
        self.check_interval = 300  # 5分钟检查一次
    
    def get_rate_limit_info(self) -> Dict[str, Any]:
        """
        获取当前速率限制信息
        
        Returns:
            速率限制信息字典
        """
        try:
            rate_limit = self.client.get_rate_limit()
            return {
                'core': {
                    'limit': rate_limit.core.limit,
                    'remaining': rate_limit.core.remaining,
                    'reset': rate_limit.core.reset.timestamp()
                },
                'search': {
                    'limit': rate_limit.search.limit,
                    'remaining': rate_limit.search.remaining,
                    'reset': rate_limit.search.reset.timestamp()
                },
                'graphql': {
                    'limit': rate_limit.graphql.limit,
                    'remaining': rate_limit.graphql.remaining,
                    'reset': rate_limit.graphql.reset.timestamp()
                }
            }
        except Exception as e:
            logger.error(f"获取速率限制信息失败: {e}")
            return {}
    
    def check_rate_limit(self, threshold: int = 100) -> bool:
        """
        检查是否接近速率限制
        
        Args:
            threshold: 剩余请求数阈值
            
        Returns:
            是否安全继续请求
        """
        current_time = time.time()
        
        # 限制检查频率
        if current_time - self.last_check_time < self.check_interval:
            return True
        
        try:
            rate_limit_info = self.get_rate_limit_info()
            core_remaining = rate_limit_info.get('core', {}).get('remaining', 0)
            
            self.last_check_time = current_time
            
            if core_remaining < threshold:
                logger.warning(f"API请求配额即将用完: {core_remaining} 次剩余")
                return False
                
            logger.info(f"API请求配额充足: {core_remaining} 次剩余")
            return True
            
        except Exception as e:
            logger.error(f"检查速率限制失败: {e}")
            return True  # 检查失败时假设安全


class GitHubClient:
    """
    GitHub API客户端封装类
    
    提供高级API操作，包括速率限制处理、错误处理和重试机制
    """
    
    def __init__(self, auth: GitHubAuth):
        """
        初始化GitHub客户端
        
        Args:
            auth: GitHub认证对象
        """
        self.auth = auth
        self.client = auth.client
        
        if not self.client:
            raise ValueError("GitHub客户端初始化失败，请检查认证配置")
        
        self.rate_limiter = RateLimitHandler(self.client)
        logger.info("GitHub客户端初始化成功")
    
    @handle_rate_limit
    def get_authenticated_user(self):
        """
        获取当前认证用户信息
        
        Returns:
            当前用户对象
        """
        return self.client.get_user()
    
    @handle_rate_limit
    def get_user_starred(self) -> PaginatedList[Repository]:
        """
        获取用户的星标项目列表
        
        Returns:
            星标项目的分页列表
        """
        user = self.get_authenticated_user()
        return user.get_starred()
    
    @handle_rate_limit
    def get_repository(self, full_name: str) -> Repository:
        """
        根据完整名称获取仓库信息
        
        Args:
            full_name: 仓库完整名称 (owner/repo)
            
        Returns:
            仓库对象
        """
        return self.client.get_repo(full_name)
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """
        获取API速率限制状态
        
        Returns:
            速率限制状态信息
        """
        return self.rate_limiter.get_rate_limit_info()
    
    def test_connection(self) -> bool:
        """
        测试GitHub API连接
        
        Returns:
            连接是否成功
        """
        try:
            user = self.get_authenticated_user()
            rate_info = self.get_rate_limit_status()
            
            logger.info(f"GitHub连接测试成功 - 用户: {user.login}")
            logger.info(f"API配额: {rate_info.get('core', {}).get('remaining', 'Unknown')}")
            
            return True
        except Exception as e:
            logger.error(f"GitHub连接测试失败: {e}")
            return False
