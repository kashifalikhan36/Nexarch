"""Caching layer for expensive operations"""
from functools import lru_cache
from typing import Optional, Any
import json
import hashlib
from datetime import datetime, timedelta


class CacheManager:
    """Simple in-memory cache (use Redis in production)"""
    
    def __init__(self, ttl_seconds: int = 300):
        self._cache = {}
        self.ttl_seconds = ttl_seconds
    
    def _generate_key(self, tenant_id: str, operation: str, **kwargs) -> str:
        """Generate cache key"""
        params = json.dumps(kwargs, sort_keys=True)
        return f"{tenant_id}:{operation}:{hashlib.md5(params.encode()).hexdigest()}"
    
    def get(self, tenant_id: str, operation: str, **kwargs) -> Optional[Any]:
        """Get from cache"""
        key = self._generate_key(tenant_id, operation, **kwargs)
        
        if key in self._cache:
            cached_data, cached_time = self._cache[key]
            
            # Check if expired
            if datetime.utcnow() - cached_time < timedelta(seconds=self.ttl_seconds):
                return cached_data
            else:
                del self._cache[key]
        
        return None
    
    def set(self, tenant_id: str, operation: str, data: Any, **kwargs):
        """Set cache"""
        key = self._generate_key(tenant_id, operation, **kwargs)
        self._cache[key] = (data, datetime.utcnow())
    
    def invalidate(self, tenant_id: str):
        """Invalidate all cache for tenant"""
        keys_to_delete = [k for k in self._cache.keys() if k.startswith(f"{tenant_id}:")]
        for key in keys_to_delete:
            del self._cache[key]
    
    def clear(self):
        """Clear entire cache"""
        self._cache.clear()


# Global cache instance
cache_manager = CacheManager(ttl_seconds=300)  # 5 minute TTL
