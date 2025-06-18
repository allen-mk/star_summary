"""
GitHub API集成模块

提供GitHub API的高级封装，包括客户端、获取器和缓存管理
"""

from .client import GitHubClient, RateLimitHandler, handle_rate_limit
from .fetcher import StarredFetcher
from .service import GitHubService, create_github_service

__all__ = [
    'GitHubClient',
    'RateLimitHandler', 
    'StarredFetcher',
    'GitHubService',
    'create_github_service',
    'handle_rate_limit'
]

__version__ = '1.0.0'