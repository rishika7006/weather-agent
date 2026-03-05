from services.providers.base import WeatherProvider
from services.lfu_cache import LFUCache


class WeatherService:
    """Provider-agnostic weather service with LFU caching.

    Delegates all API calls to a pluggable WeatherProvider and wraps
    them with a cache-aside caching layer.
    """

    def __init__(self, provider: WeatherProvider):
        self.provider = provider
        self.cache = LFUCache(capacity=128, ttl_seconds=300)

    async def get_current_weather(self, city: str) -> tuple[dict, bool]:
        cache_key = f"current:{city.lower().strip()}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached, True

        result = await self.provider.get_current_weather(city)
        self.cache.put(cache_key, result)
        return result, False

    async def get_forecast(self, city: str, days: int = 3) -> tuple[dict, bool]:
        cache_key = f"forecast:{city.lower().strip()}:{days}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached, True

        result = await self.provider.get_forecast(city, days)
        self.cache.put(cache_key, result)
        return result, False

    async def get_air_quality(self, city: str) -> tuple[dict, bool]:
        cache_key = f"air:{city.lower().strip()}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached, True

        result = await self.provider.get_air_quality(city)
        self.cache.put(cache_key, result)
        return result, False
