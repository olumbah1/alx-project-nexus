from django.core.cache import cache
from django.conf import settings
from functools import wraps
import hashlib


def make_cache_key(prefix, *args, **kwargs):
    """Generate a unique cache key from arguments"""
    key_data = f"{prefix}:{args}:{sorted(kwargs.items())}"
    return hashlib.md5(key_data.encode()).hexdigest()


def invalidate_cache_pattern(pattern):
    """Invalidate all cache keys matching a pattern"""
    try:
        from django_redis import get_redis_connection
        conn = get_redis_connection("default")
        keys = conn.keys(f"*{pattern}*")
        if keys:
            conn.delete(*keys)
    except Exception as e:
        # Fallback: clear all cache
        print(f"Cache invalidation error: {e}")
        cache.clear()