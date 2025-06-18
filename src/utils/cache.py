"""
缓存管理工具

提供星标项目数据的本地缓存功能，避免重复API请求
"""

import os
import json
import pickle
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path


logger = logging.getLogger(__name__)


class RepoCache:
    """
    仓库数据缓存管理器
    
    支持JSON和Pickle两种缓存格式，提供缓存有效性检查和清理功能
    """
    
    def __init__(self, cache_dir: str = "cache", cache_format: str = "json"):
        """
        初始化缓存管理器
        
        Args:
            cache_dir: 缓存目录路径
            cache_format: 缓存格式 ('json' 或 'pickle')
        """
        self.cache_dir = Path(cache_dir)
        self.cache_format = cache_format.lower()
        
        if self.cache_format not in ['json', 'pickle']:
            raise ValueError("缓存格式必须是 'json' 或 'pickle'")
        
        # 创建缓存目录
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 设置缓存文件扩展名
        self.cache_ext = '.json' if self.cache_format == 'json' else '.pkl'
        
        logger.info(f"缓存管理器初始化完成 - 目录: {self.cache_dir}, 格式: {self.cache_format}")
    
    def get_cache_file_path(self, cache_key: str) -> Path:
        """
        获取缓存文件路径
        
        Args:
            cache_key: 缓存键
            
        Returns:
            缓存文件路径
        """
        safe_key = self._sanitize_filename(cache_key)
        return self.cache_dir / f"{safe_key}{self.cache_ext}"
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        清理文件名，移除不安全字符
        
        Args:
            filename: 原始文件名
            
        Returns:
            清理后的文件名
        """
        # 替换不安全字符
        unsafe_chars = '<>:"/\\|?*'
        safe_filename = filename
        for char in unsafe_chars:
            safe_filename = safe_filename.replace(char, '_')
        
        # 限制长度
        if len(safe_filename) > 200:
            safe_filename = safe_filename[:200]
        
        return safe_filename
    
    def save_repos(self, repos: List[Dict[str, Any]], cache_key: str, 
                   metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        保存仓库数据到缓存
        
        Args:
            repos: 仓库数据列表
            cache_key: 缓存键
            metadata: 额外元数据
            
        Returns:
            是否保存成功
        """
        try:
            cache_file = self.get_cache_file_path(cache_key)
            
            # 准备缓存数据
            cache_data = {
                'repos': repos,
                'metadata': metadata or {},
                'cached_at': datetime.now().isoformat(),
                'cache_version': '1.0',
                'repo_count': len(repos)
            }
            
            # 根据格式保存
            if self.cache_format == 'json':
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(cache_data, f, indent=2, ensure_ascii=False, default=str)
            else:  # pickle
                with open(cache_file, 'wb') as f:
                    pickle.dump(cache_data, f)
            
            logger.info(f"缓存保存成功: {cache_file} ({len(repos)} 个项目)")
            return True
            
        except Exception as e:
            logger.error(f"保存缓存失败: {e}")
            return False
    
    def load_repos(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        从缓存加载仓库数据
        
        Args:
            cache_key: 缓存键
            
        Returns:
            缓存数据字典，如果不存在或加载失败则返回None
        """
        try:
            cache_file = self.get_cache_file_path(cache_key)
            
            if not cache_file.exists():
                logger.debug(f"缓存文件不存在: {cache_file}")
                return None
            
            # 根据格式加载
            if self.cache_format == 'json':
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
            else:  # pickle
                with open(cache_file, 'rb') as f:
                    cache_data = pickle.load(f)
            
            logger.info(f"缓存加载成功: {cache_file} ({cache_data.get('repo_count', 0)} 个项目)")
            return cache_data
            
        except Exception as e:
            logger.error(f"加载缓存失败: {e}")
            return None
    
    def is_cache_valid(self, cache_key: str, max_age_hours: int = 24) -> bool:
        """
        检查缓存是否有效
        
        Args:
            cache_key: 缓存键
            max_age_hours: 最大缓存时间（小时）
            
        Returns:
            缓存是否有效
        """
        try:
            cache_data = self.load_repos(cache_key)
            if not cache_data:
                return False
            
            cached_at_str = cache_data.get('cached_at')
            if not cached_at_str:
                return False
            
            cached_at = datetime.fromisoformat(cached_at_str)
            max_age = timedelta(hours=max_age_hours)
            
            is_valid = datetime.now() - cached_at < max_age
            
            if is_valid:
                logger.debug(f"缓存有效: {cache_key}")
            else:
                logger.debug(f"缓存过期: {cache_key}")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"检查缓存有效性失败: {e}")
            return False
    
    def get_cache_info(self, cache_key: str) -> Dict[str, Any]:
        """
        获取缓存信息
        
        Args:
            cache_key: 缓存键
            
        Returns:
            缓存信息字典
        """
        info = {
            'cache_key': cache_key,
            'exists': False,
            'valid': False,
            'file_path': str(self.get_cache_file_path(cache_key))
        }
        
        try:
            cache_file = self.get_cache_file_path(cache_key)
            
            if cache_file.exists():
                info['exists'] = True
                info['file_size'] = cache_file.stat().st_size
                info['file_mtime'] = datetime.fromtimestamp(cache_file.stat().st_mtime).isoformat()
                
                cache_data = self.load_repos(cache_key)
                if cache_data:
                    info.update({
                        'repo_count': cache_data.get('repo_count', 0),
                        'cached_at': cache_data.get('cached_at'),
                        'cache_version': cache_data.get('cache_version'),
                        'metadata': cache_data.get('metadata', {})
                    })
                    
                    info['valid'] = self.is_cache_valid(cache_key)
        
        except Exception as e:
            info['error'] = str(e)
        
        return info
    
    def clear_cache(self, cache_key: Optional[str] = None) -> bool:
        """
        清理缓存
        
        Args:
            cache_key: 指定清理的缓存键，如果为None则清理所有缓存
            
        Returns:
            是否清理成功
        """
        try:
            if cache_key:
                # 清理指定缓存
                cache_file = self.get_cache_file_path(cache_key)
                if cache_file.exists():
                    cache_file.unlink()
                    logger.info(f"已清理缓存: {cache_file}")
                    return True
                else:
                    logger.warning(f"缓存文件不存在: {cache_file}")
                    return False
            else:
                # 清理所有缓存
                deleted_count = 0
                for cache_file in self.cache_dir.glob(f"*{self.cache_ext}"):
                    cache_file.unlink()
                    deleted_count += 1
                
                logger.info(f"已清理 {deleted_count} 个缓存文件")
                return True
                
        except Exception as e:
            logger.error(f"清理缓存失败: {e}")
            return False
    
    def list_cache_files(self) -> List[Dict[str, Any]]:
        """
        列出所有缓存文件
        
        Returns:
            缓存文件信息列表
        """
        cache_files = []
        
        try:
            for cache_file in self.cache_dir.glob(f"*{self.cache_ext}"):
                cache_key = cache_file.stem
                info = self.get_cache_info(cache_key)
                cache_files.append(info)
        
        except Exception as e:
            logger.error(f"列出缓存文件失败: {e}")
        
        return cache_files
    
    def cleanup_expired_cache(self, max_age_hours: int = 24) -> int:
        """
        清理过期缓存
        
        Args:
            max_age_hours: 最大缓存时间（小时）
            
        Returns:
            清理的文件数量
        """
        cleaned_count = 0
        
        try:
            for cache_file in self.cache_dir.glob(f"*{self.cache_ext}"):
                cache_key = cache_file.stem
                if not self.is_cache_valid(cache_key, max_age_hours):
                    cache_file.unlink()
                    cleaned_count += 1
                    logger.debug(f"已清理过期缓存: {cache_file}")
            
            if cleaned_count > 0:
                logger.info(f"清理了 {cleaned_count} 个过期缓存文件")
        
        except Exception as e:
            logger.error(f"清理过期缓存失败: {e}")
        
        return cleaned_count


class CacheManager:
    """
    缓存管理器的高级接口
    
    提供更便捷的缓存操作方法，支持多种缓存策略
    """
    
    def __init__(self, cache_dir: str = "cache", cache_format: str = "json"):
        """
        初始化缓存管理器
        
        Args:
            cache_dir: 缓存目录
            cache_format: 缓存格式
        """
        self.cache = RepoCache(cache_dir, cache_format)
    
    def get_user_cache_key(self, username: str) -> str:
        """
        生成用户缓存键
        
        Args:
            username: GitHub用户名
            
        Returns:
            缓存键
        """
        return f"starred_repos_{username}"
    
    def save_starred_repos(self, username: str, repos: List[Dict[str, Any]], 
                          metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        保存用户星标项目
        
        Args:
            username: GitHub用户名
            repos: 仓库数据列表
            metadata: 额外元数据
            
        Returns:
            是否保存成功
        """
        cache_key = self.get_user_cache_key(username)
        return self.cache.save_repos(repos, cache_key, metadata)
    
    def load_starred_repos(self, username: str) -> Optional[List[Dict[str, Any]]]:
        """
        加载用户星标项目
        
        Args:
            username: GitHub用户名
            
        Returns:
            仓库数据列表
        """
        cache_key = self.get_user_cache_key(username)
        cache_data = self.cache.load_repos(cache_key)
        
        if cache_data:
            return cache_data.get('repos', [])
        
        return None
    
    def is_user_cache_valid(self, username: str, max_age_hours: int = 24) -> bool:
        """
        检查用户缓存是否有效
        
        Args:
            username: GitHub用户名
            max_age_hours: 最大缓存时间（小时）
            
        Returns:
            缓存是否有效
        """
        cache_key = self.get_user_cache_key(username)
        return self.cache.is_cache_valid(cache_key, max_age_hours)
