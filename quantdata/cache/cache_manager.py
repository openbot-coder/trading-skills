"""
缓存管理器 - 提供可配置的过期时间的缓存功能
"""

import time
import hashlib
import json
import os
import logging
from typing import Any, Callable, Optional, Dict, List
from pathlib import Path
from functools import wraps

logger = logging.getLogger(__name__)


class CacheEntry:
    """缓存条目"""
    def __init__(self, data: Any, expire_at: float):
        self.data = data
        self.expire_at = expire_at
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        return time.time() > self.expire_at


class CacheManager:
    """
    缓存管理器
    
    支持内存缓存，可配置不同类型数据的过期时间
    """
    
    # 默认缓存时间（秒）
    DEFAULT_CACHE_REALTIME_A_SHARE = 3  # A股实时行情3秒
    DEFAULT_CACHE_REALTIME_OTHER = 1    # 其他实时行情1秒
    DEFAULT_CACHE_NORMAL = 3600         # 其他数据1小时
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        初始化缓存管理器
        
        Args:
            cache_dir: 缓存目录，可选。如果不提供则仅使用内存缓存
        """
        # 内存缓存
        self._memory_cache: Dict[str, CacheEntry] = {}
        
        # 文件缓存目录
        self._cache_dir = None
        if cache_dir:
            self._cache_dir = Path(cache_dir)
            self._cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_key(self, namespace: str, key: str) -> str:
        """
        生成缓存键
        
        Args:
            namespace: 命名空间，用于区分不同类型的数据
            key: 数据键
            
        Returns:
            完整的缓存键
        """
        combined = f"{namespace}:{key}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _get_file_path(self, cache_key: str) -> Path:
        """获取缓存文件路径"""
        if not self._cache_dir:
            raise ValueError("File cache not enabled")
        return self._cache_dir / f"{cache_key}.json"
    
    def get(self, namespace: str, key: str) -> Optional[Any]:
        """
        获取缓存数据
        
        Args:
            namespace: 命名空间
            key: 数据键
            
        Returns:
            缓存的数据，如果没有或过期则返回None
        """
        cache_key = self._get_cache_key(namespace, key)
        
        # 首先检查内存缓存
        if cache_key in self._memory_cache:
            entry = self._memory_cache[cache_key]
            if not entry.is_expired():
                return entry.data
            # 过期了，删除
            del self._memory_cache[cache_key]
        
        # 检查文件缓存
        if self._cache_dir:
            file_path = self._get_file_path(cache_key)
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        expire_at = data.get('__expire_at', 0)
                        if time.time() <= expire_at:
                            # 恢复到内存缓存
                            self._memory_cache[cache_key] = CacheEntry(data['data'], expire_at)
                            return data['data']
                        else:
                            # 过期，删除文件
                            file_path.unlink()
                except (IOError, json.JSONDecodeError) as e:
                    logger.warning(f"缓存文件读取失败，已删除: {file_path}, 错误: {e}")
                    try:
                        file_path.unlink()
                    except OSError:
                        pass
        
        return None
    
    def set(self, namespace: str, key: str, data: Any, ttl: int):
        """
        设置缓存数据
        
        Args:
            namespace: 命名空间
            key: 数据键
            data: 要缓存的数据
            ttl: 过期时间（秒）
        """
        cache_key = self._get_cache_key(namespace, key)
        expire_at = time.time() + ttl
        
        # 内存缓存
        self._memory_cache[cache_key] = CacheEntry(data, expire_at)
        
        # 文件缓存
        if self._cache_dir:
            try:
                file_path = self._get_file_path(cache_key)
                cache_data = {
                    'data': data,
                    '__expire_at': expire_at
                }
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(cache_data, f, ensure_ascii=False)
            except (IOError, TypeError) as e:
                logger.warning(f"缓存写入失败: {e}")
    
    def delete(self, namespace: str, key: str):
        """删除缓存数据"""
        cache_key = self._get_cache_key(namespace, key)
        
        if cache_key in self._memory_cache:
            del self._memory_cache[cache_key]
        
        if self._cache_dir:
            file_path = self._get_file_path(cache_key)
            if file_path.exists():
                try:
                    file_path.unlink()
                except:
                    pass
    
    def clear(self, namespace: Optional[str] = None):
        """
        清空缓存
        
        Args:
            namespace: 如果提供则只清空该命名空间的缓存
        """
        if namespace:
            # 清空特定命名空间
            keys_to_delete = []
            for key in self._memory_cache.keys():
                if key.startswith(self._get_cache_key(namespace, '')[:16]):
                    keys_to_delete.append(key)
            for key in keys_to_delete:
                del self._memory_cache[key]
            
            if self._cache_dir:
                for file in self._cache_dir.glob("*.json"):
                    try:
                        file.unlink()
                    except:
                        pass
        else:
            # 清空全部
            self._memory_cache.clear()
            if self._cache_dir:
                for file in self._cache_dir.glob("*.json"):
                    try:
                        file.unlink()
                    except:
                        pass
    
    def cached(self, namespace: str, ttl: int, key_func: Optional[Callable] = None):
        """
        装饰器：缓存函数返回值
        
        Args:
            namespace: 命名空间
            ttl: 过期时间（秒）
            key_func: 自定义键生成函数，接收和原函数相同的参数
            
        Returns:
            装饰器函数
        """
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # 生成缓存键
                if key_func:
                    key = key_func(*args, **kwargs)
                else:
                    key_parts = [str(args), str(sorted(kwargs.items()))]
                    key = hashlib.md5("|".join(key_parts).encode()).hexdigest()
                
                # 尝试获取缓存
                cached_data = self.get(namespace, key)
                if cached_data is not None:
                    return cached_data
                
                # 执行函数
                result = func(*args, **kwargs)
                
                # 保存缓存
                self.set(namespace, key, result, ttl)
                
                return result
            return wrapper
        return decorator


# 全局缓存实例
_global_cache: Optional[CacheManager] = None


def get_cache() -> CacheManager:
    """
    获取全局缓存管理器实例
    
    Returns:
        全局缓存管理器
    """
    global _global_cache
    if _global_cache is None:
        # 默认缓存目录在用户目录下
        cache_dir = os.path.join(os.path.expanduser("~"), ".quantdata_cache")
        _global_cache = CacheManager(cache_dir=cache_dir)
    return _global_cache


def determine_ttl(market_type: str, data_type: str) -> int:
    """
    根据市场和数据类型确定TTL
    
    Args:
        market_type: 市场类型，如 "A_share", "other"
        data_type: 数据类型，如 "realtime", "kline", "financial"
        
    Returns:
        TTL（秒）
    """
    if data_type == "realtime":
        if market_type == "A_share":
            return CacheManager.DEFAULT_CACHE_REALTIME_A_SHARE
        else:
            return CacheManager.DEFAULT_CACHE_REALTIME_OTHER
    else:
        return CacheManager.DEFAULT_CACHE_NORMAL
