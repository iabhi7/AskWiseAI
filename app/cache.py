import time
from typing import Dict, Any, Optional, Tuple
import hashlib
import json

class SimpleCache:
    """A simple in-memory cache with time-based expiration."""
    
    def __init__(self, default_ttl: int = 300):
        """
        Initialize the cache.
        
        Args:
            default_ttl: Default time-to-live in seconds (5 minutes)
        """
        self.cache: Dict[str, Tuple[Any, float]] = {}
        self.default_ttl = default_ttl
    
    def _get_key(self, data: Any) -> str:
        """Generate a cache key from the data."""
        if isinstance(data, str):
            serialized = data
        else:
            serialized = json.dumps(data, sort_keys=True)
        
        return hashlib.md5(serialized.encode('utf-8')).hexdigest()
    
    def get(self, key_data: Any) -> Optional[Any]:
        """
        Get a value from the cache.
        
        Args:
            key_data: Data to generate the key from
            
        Returns:
            The cached value or None if not found or expired
        """
        key = self._get_key(key_data)
        
        if key in self.cache:
            value, expiry = self.cache[key]
            
            # Check if the entry has expired
            if time.time() < expiry:
                print(f"Cache hit for key: {key}")
                return value
            
            # Remove expired entry
            print(f"Cache expired for key: {key}")
            del self.cache[key]
        
        print(f"Cache miss for key: {key}")
        return None
    
    def set(self, key_data: Any, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set a value in the cache.
        
        Args:
            key_data: Data to generate the key from
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if None)
        """
        key = self._get_key(key_data)
        expiry = time.time() + (ttl if ttl is not None else self.default_ttl)
        self.cache[key] = (value, expiry)
        print(f"Cached value for key: {key}, expires in {ttl if ttl is not None else self.default_ttl}s")
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()
        print("Cache cleared")
    
    def remove_expired(self) -> int:
        """
        Remove all expired entries from the cache.
        
        Returns:
            Number of entries removed
        """
        now = time.time()
        expired_keys = [k for k, (_, exp) in self.cache.items() if now > exp]
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            print(f"Removed {len(expired_keys)} expired cache entries")
        
        return len(expired_keys)

# Create cache instances
llm_cache = SimpleCache(default_ttl=3600)  # 1 hour for LLM responses
tool_cache = SimpleCache(default_ttl=300)  # 5 minutes for tool responses 