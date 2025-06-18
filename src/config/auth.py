"""
GitHub认证管理模块

负责GitHub API的认证和客户端管理。
"""

import os
from typing import Optional
from github import Github, Auth
from .settings import Config


class GitHubAuth:
    """GitHub认证管理类"""
    
    def __init__(self, config: Config):
        """
        初始化GitHub认证
        
        Args:
            config: 配置管理对象
        """
        self.config = config
        self.token = self._get_token()
        self.client = self._create_client()
    
    def _get_token(self) -> Optional[str]:
        """
        获取GitHub Token
        
        Returns:
            GitHub Token或None
        """
        return self.config.github_token
    
    def _create_client(self) -> Optional[Github]:
        """
        创建GitHub客户端
        
        Returns:
            GitHub客户端实例或None
        """
        if not self.token:
            print("错误: 未找到GitHub Token")
            return None
        
        try:
            # 使用Token认证创建客户端
            auth = Auth.Token(self.token)
            base_url = self.config.get('github.api_base_url', 'https://api.github.com')
            
            client = Github(auth=auth, base_url=base_url)
            
            # 验证认证是否有效
            user = client.get_user()
            print(f"GitHub认证成功: {user.login}")
            
            return client
            
        except Exception as e:
            print(f"GitHub认证失败: {e}")
            return None
    
    def get_client(self) -> Optional[Github]:
        """
        获取GitHub客户端
        
        Returns:
            GitHub客户端实例
        """
        return self.client
    
    def is_authenticated(self) -> bool:
        """
        检查是否已认证
        
        Returns:
            是否已认证
        """
        return self.client is not None
    
    def get_rate_limit(self) -> dict:
        """
        获取API速率限制信息
        
        Returns:
            速率限制信息字典
        """
        if not self.client:
            return {'error': 'Not authenticated'}
        
        try:
            rate_limit = self.client.get_rate_limit()
            return {
                'core': {
                    'limit': rate_limit.core.limit,
                    'remaining': rate_limit.core.remaining,
                    'reset': rate_limit.core.reset.isoformat()
                },
                'search': {
                    'limit': rate_limit.search.limit,
                    'remaining': rate_limit.search.remaining,
                    'reset': rate_limit.search.reset.isoformat()
                }
            }
        except Exception as e:
            return {'error': f'Failed to get rate limit: {e}'}
    
    def get_user_info(self) -> dict:
        """
        获取当前用户信息
        
        Returns:
            用户信息字典
        """
        if not self.client:
            return {'error': 'Not authenticated'}
        
        try:
            user = self.client.get_user()
            return {
                'login': user.login,
                'name': user.name,
                'email': user.email,
                'public_repos': user.public_repos,
                'followers': user.followers,
                'following': user.following
            }
        except Exception as e:
            return {'error': f'Failed to get user info: {e}'}
    
    def test_connection(self) -> bool:
        """
        测试GitHub连接
        
        Returns:
            连接是否成功
        """
        if not self.client:
            print("GitHub客户端未初始化")
            return False
        
        try:
            user = self.client.get_user()
            rate_limit = self.get_rate_limit()
            
            print(f"✅ GitHub连接测试成功")
            print(f"   用户: {user.login}")
            print(f"   API限制: {rate_limit['core']['remaining']}/{rate_limit['core']['limit']}")
            
            return True
            
        except Exception as e:
            print(f"❌ GitHub连接测试失败: {e}")
            return False
