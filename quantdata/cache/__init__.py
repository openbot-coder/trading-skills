"""
数据缓存模块 - 为财经数据提供缓存功能
实时行情缓存：A股3秒，其他1秒
其他数据缓存：1小时
"""

from .cache_manager import CacheManager, get_cache, determine_ttl

__all__ = ['CacheManager', 'get_cache', 'determine_ttl']
