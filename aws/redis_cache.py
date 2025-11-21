# redis_cache.py

import redis
import json
from datetime import datetime
from typing import List, Dict, Optional

class ClinicalTrialsCache:
    """Redis cache manager for clinical trials data"""
    
    def __init__(self, host='localhost', port=6379):
        self.redis_client = redis.Redis(
            host=host,
            port=port,
            decode_responses=True
        )
        self.default_ttl = 3600  # 1 hour
    
    def ping(self):
        """Check Redis connection"""
        try:
            return self.redis_client.ping()
        except:
            return False
    
    def cache_studies(self, condition: str, studies: List[Dict], ttl: int = None):
        """Cache clinical trials by condition"""
        key = f"trials:{condition.lower()}"
        
        self.redis_client.set(
            key,
            json.dumps(studies),
            ex=ttl or self.default_ttl
        )
        
        print(f"✓ Cached {len(studies)} studies for '{condition}'")
        return key
    
    def get_studies(self, condition: str) -> Optional[List[Dict]]:
        """Retrieve cached studies by condition"""
        key = f"trials:{condition.lower()}"
        cached = self.redis_client.get(key)
        
        if cached:
            studies = json.loads(cached)
            print(f"✓ Retrieved {len(studies)} studies from cache: '{condition}'")
            return studies
        
        return None
    
    def cache_all_studies(self, studies: List[Dict], ttl: int = None):
        """Cache all studies under master key"""
        key = "trials:all"
        
        self.redis_client.set(
            key,
            json.dumps(studies),
            ex=ttl or self.default_ttl
        )
        
        print(f"✓ Cached {len(studies)} total studies")
        return key
    
    def get_all_studies(self) -> Optional[List[Dict]]:
        """Retrieve all cached studies"""
        cached = self.redis_client.get("trials:all")
        
        if cached:
            studies = json.loads(cached)
            print(f"✓ Retrieved {len(studies)} total studies from cache")
            return studies
        
        return None
    
    def cache_metadata(self, metadata: Dict):
        """Store metadata about cached data"""
        self.redis_client.set(
            "trials:metadata",
            json.dumps(metadata),
            ex=self.default_ttl
        )
    
    def get_metadata(self) -> Optional[Dict]:
        """Retrieve cached metadata"""
        cached = self.redis_client.get("trials:metadata")
        return json.loads(cached) if cached else None
    
    def get_cache_stats(self) -> Dict:
        """Get Redis cache statistics"""
        info = self.redis_client.info()
        keys = self.redis_client.keys('trials:*')
        
        return {
            "redis_version": info.get('redis_version'),
            "connected_clients": info.get('connected_clients'),
            "used_memory_human": info.get('used_memory_human'),
            "total_keys": len(keys),
            "cached_keys": [k for k in keys],
            "uptime_seconds": info.get('uptime_in_seconds')
        }
    
    def clear_cache(self):
        """Clear all cached trial data"""
        keys = self.redis_client.keys('trials:*')
        if keys:
            self.redis_client.delete(*keys)
            print(f"✓ Cleared {len(keys)} cached keys")


# Quick test
if __name__ == "__main__":
    cache = ClinicalTrialsCache()
    
    if cache.ping():
        print("✓ Redis connection successful")
        
        # Test caching
        test_data = [
            {"nct_id": "NCT001", "title": "Test Study 1"},
            {"nct_id": "NCT002", "title": "Test Study 2"}
        ]
        
        cache.cache_studies("cancer", test_data)
        retrieved = cache.get_studies("cancer")
        print(f"Retrieved: {retrieved}")
        
        stats = cache.get_cache_stats()
        print(f"\nCache stats: {stats}")
    else:
        print("✗ Redis connection failed")