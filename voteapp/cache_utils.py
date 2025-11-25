from rest_framework.response import Response
from django.core.cache import cache
from django.conf import settings
from functools import wraps
import hashlib
import json


def make_cache_key(prefix, *args, **kwargs):
    """Generate a unique cache key from arguments"""
    key_data = f"{prefix}:{args}:{sorted(kwargs.items())}"
    return hashlib.md5(key_data.encode()).hexdigest()


def cache_response(timeout=None, key_prefix='view'):
    """
    Decorator to cache view responses
    Usage: @cache_response(timeout=300, key_prefix='polls')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(self, request, *args, **kwargs):
            # Generate cache key from request parameters
            cache_key = make_cache_key(
                key_prefix,
                request.path,
                request.GET.dict(),
                args,
                kwargs
            )
            
            # Try to get from cache
            cached_response = cache.get(cache_key)
            if cached_response is not None:
                return Response(cached_response)
            
            # Get fresh response
            response = view_func(self, request, *args, **kwargs)
            
            # Cache the response data
            if response.status_code == 200:
                cache_timeout = timeout or settings.CACHE_TTL.get(key_prefix, 300)
                cache.set(cache_key, response.data, cache_timeout)
            
            return response
        return wrapper
    return decorator


def invalidate_cache_pattern(pattern):
    """Invalidate all cache keys matching a pattern"""
    # Note: This requires django-redis backend
    try:
        from django_redis import get_redis_connection
        conn = get_redis_connection("default")
        keys = conn.keys(f"*{pattern}*")
        if keys:
            conn.delete(*keys)
    except ImportError:
        # Fallback if django-redis not available
        cache.clear()