import asyncio
import json
import hashlib
from typing import Any, Optional
from redis import asyncio as aioredis
from .config import settings


class RedisCache:
    _client: Optional[aioredis.Redis] = None

    def __init__(self, redis_url: str = settings.REDIS_URL, default_ttl: int = 300):
        self.redis_url = redis_url
        self.default_ttl = default_ttl

    async def get_client(self) -> aioredis.Redis:
        await asyncio.sleep(0)
        if not self._client:
            self._client = aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
        return self._client

    async def close_client(self):
        if self._client:
            await self._client.close()
            self._client = None

    @staticmethod
    def generate_cache_key(prefix: str, **kwargs) -> str:
        sorted_params = sorted(kwargs.items())
        params_str = json.dumps(sorted_params, sort_keys=True)
        hash_suffix = hashlib.md5(params_str.encode()).hexdigest()
        return f"{prefix}:{hash_suffix}"

    async def get(self, key: str) -> Optional[Any]:
        try:
            client = await self.get_client()
            cached = await client.get(key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            print(f"Cache get error: {e}")
        return None

    async def set(self, key: str, data: Any, ttl: Optional[int] = None) -> bool:
        try:
            client = await self.get_client()
            serialized = json.dumps(data, default=str)
            await client.setex(key, ttl or self.default_ttl, serialized)
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False

    async def invalidate(self, pattern: str = None, key: str = None):
        try:
            client = await self.get_client()
            if key:
                await client.delete(key)
            elif pattern:
                keys = await client.keys(pattern)
                if keys:
                    await client.delete(*keys)
        except Exception as e:
            print(f"Cache invalidation error: {e}")
