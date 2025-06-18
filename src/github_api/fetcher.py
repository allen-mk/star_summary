"""
GitHub 星标项目获取器

负责获取用户的所有星标项目，处理分页和数据提取，提供进度显示
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from github.Repository import Repository
from github.PaginatedList import PaginatedList
from tqdm import tqdm

from .client import GitHubClient


logger = logging.getLogger(__name__)


class StarredFetcher:
    """
    星标项目获取器
    
    负责从GitHub API获取用户的所有星标项目，处理分页和数据提取
    """
    
    def __init__(self, github_client: GitHubClient):
        """
        初始化获取器
        
        Args:
            github_client: GitHub API客户端
        """
        self.client = github_client
        
    def fetch_all_starred(self, show_progress: bool = True) -> List[Dict[str, Any]]:
        """
        获取所有星标项目
        
        Args:
            show_progress: 是否显示进度条
            
        Returns:
            星标项目数据列表
        """
        logger.info("开始获取星标项目...")
        
        try:
            # 获取星标项目的分页列表
            starred_repos = self.client.get_user_starred()
            
            # 首先获取总数（如果可能）
            total_count = self._get_total_count(starred_repos)
            
            repos_data = []
            
            if show_progress and total_count:
                # 使用已知总数的进度条
                progress_bar = tqdm(total=total_count, desc="获取星标项目", unit="repos")
            elif show_progress:
                # 使用无限进度条
                progress_bar = tqdm(desc="获取星标项目", unit="repos")
            else:
                progress_bar = None
            
            # 遍历所有星标项目
            for repo in starred_repos:
                try:
                    repo_data = self.extract_repo_data(repo)
                    repos_data.append(repo_data)
                    
                    if progress_bar:
                        progress_bar.update(1)
                        progress_bar.set_postfix({
                            'current': repo.full_name,
                            'total': len(repos_data)
                        })
                    
                except Exception as e:
                    logger.warning(f"提取项目 {repo.full_name} 数据失败: {e}")
                    continue
            
            if progress_bar:
                progress_bar.close()
            
            logger.info(f"成功获取 {len(repos_data)} 个星标项目")
            return repos_data
            
        except Exception as e:
            logger.error(f"获取星标项目失败: {e}")
            raise
    
    def _get_total_count(self, paginated_list: PaginatedList) -> Optional[int]:
        """
        尝试获取分页列表的总数
        
        Args:
            paginated_list: GitHub分页列表
            
        Returns:
            总数（如果可获取）
        """
        try:
            # PyGithub的PaginatedList有时包含totalCount属性
            if hasattr(paginated_list, 'totalCount'):
                return paginated_list.totalCount
        except:
            pass
        
        return None
    
    def extract_repo_data(self, repo: Repository) -> Dict[str, Any]:
        """
        提取仓库数据
        
        Args:
            repo: GitHub仓库对象
            
        Returns:
            仓库数据字典
        """
        try:
            # 安全获取属性值
            def safe_get(attr_name, default=None):
                try:
                    value = getattr(repo, attr_name, default)
                    return value if value is not None else default
                except:
                    return default
            
            # 提取基本信息
            repo_data = {
                'id': safe_get('id'),
                'name': safe_get('name', ''),
                'full_name': safe_get('full_name', ''),
                'description': safe_get('description', ''),
                'html_url': safe_get('html_url', ''),
                'clone_url': safe_get('clone_url', ''),
                'ssh_url': safe_get('ssh_url', ''),
                'homepage': safe_get('homepage', ''),
                
                # 仓库属性
                'private': safe_get('private', False),
                'fork': safe_get('fork', False),
                'archived': safe_get('archived', False),
                'disabled': safe_get('disabled', False),
                
                # 统计信息
                'stargazers_count': safe_get('stargazers_count', 0),
                'watchers_count': safe_get('watchers_count', 0),
                'forks_count': safe_get('forks_count', 0),
                'open_issues_count': safe_get('open_issues_count', 0),
                'size': safe_get('size', 0),
                
                # 语言和主题
                'language': safe_get('language', ''),
                'topics': self._safe_get_topics(repo),
                
                # 时间信息
                'created_at': self._safe_get_datetime(repo, 'created_at'),
                'updated_at': self._safe_get_datetime(repo, 'updated_at'),
                'pushed_at': self._safe_get_datetime(repo, 'pushed_at'),
                
                # 许可证信息
                'license': self._safe_get_license(repo),
                
                # 拥有者信息
                'owner': self._safe_get_owner(repo),
                
                # 获取时间
                'fetched_at': datetime.now().isoformat()
            }
            
            return repo_data
            
        except Exception as e:
            logger.error(f"提取仓库 {repo.full_name} 数据时出错: {e}")
            # 返回基本信息
            return {
                'id': getattr(repo, 'id', None),
                'name': getattr(repo, 'name', ''),
                'full_name': getattr(repo, 'full_name', ''),
                'description': getattr(repo, 'description', ''),
                'html_url': getattr(repo, 'html_url', ''),
                'language': getattr(repo, 'language', ''),
                'error': str(e),
                'fetched_at': datetime.now().isoformat()
            }
    
    def _safe_get_topics(self, repo: Repository) -> List[str]:
        """
        安全获取仓库主题
        
        Args:
            repo: 仓库对象
            
        Returns:
            主题列表
        """
        try:
            topics = getattr(repo, 'topics', [])
            return list(topics) if topics else []
        except:
            return []
    
    def _safe_get_datetime(self, repo: Repository, attr_name: str) -> Optional[str]:
        """
        安全获取日期时间属性
        
        Args:
            repo: 仓库对象
            attr_name: 属性名
            
        Returns:
            ISO格式的日期时间字符串
        """
        try:
            dt = getattr(repo, attr_name, None)
            if dt:
                return dt.isoformat()
        except:
            pass
        return None
    
    def _safe_get_license(self, repo: Repository) -> Optional[Dict[str, str]]:
        """
        安全获取许可证信息
        
        Args:
            repo: 仓库对象
            
        Returns:
            许可证信息字典
        """
        try:
            license_obj = getattr(repo, 'license', None)
            if license_obj:
                return {
                    'key': getattr(license_obj, 'key', ''),
                    'name': getattr(license_obj, 'name', ''),
                    'spdx_id': getattr(license_obj, 'spdx_id', '')
                }
        except:
            pass
        return None
    
    def _safe_get_owner(self, repo: Repository) -> Optional[Dict[str, Any]]:
        """
        安全获取仓库拥有者信息
        
        Args:
            repo: 仓库对象
            
        Returns:
            拥有者信息字典
        """
        try:
            owner = getattr(repo, 'owner', None)
            if owner:
                return {
                    'login': getattr(owner, 'login', ''),
                    'id': getattr(owner, 'id', None),
                    'type': getattr(owner, 'type', ''),
                    'avatar_url': getattr(owner, 'avatar_url', ''),
                    'html_url': getattr(owner, 'html_url', '')
                }
        except:
            pass
        return None
    
    def get_starred_summary(self) -> Dict[str, Any]:
        """
        获取星标项目摘要信息
        
        Returns:
            摘要信息字典
        """
        try:
            starred_repos = self.client.get_user_starred()
            user = self.client.get_authenticated_user()
            
            # 尝试获取总数
            total_count = self._get_total_count(starred_repos)
            if total_count is None:
                # 如果无法直接获取总数，则通过遍历计算（仅用于摘要）
                total_count = sum(1 for _ in starred_repos)
            
            return {
                'user': user.login,
                'total_starred': total_count,
                'fetched_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"获取星标项目摘要失败: {e}")
            return {
                'error': str(e),
                'fetched_at': datetime.now().isoformat()
            }
