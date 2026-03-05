import time
from unittest.mock import patch
from services.lfu_cache import LFUCache


class TestLFUCacheBasic:
    def test_get_miss_returns_none(self):
        cache = LFUCache(capacity=4)
        assert cache.get("nonexistent") is None

    def test_put_and_get(self):
        cache = LFUCache(capacity=4)
        cache.put("a", 1)
        assert cache.get("a") == 1

    def test_put_overwrites_existing_key(self):
        cache = LFUCache(capacity=4)
        cache.put("a", 1)
        cache.put("a", 2)
        assert cache.get("a") == 2

    def test_multiple_keys(self):
        cache = LFUCache(capacity=4)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)
        assert cache.get("a") == 1
        assert cache.get("b") == 2
        assert cache.get("c") == 3

    def test_zero_capacity_ignores_puts(self):
        cache = LFUCache(capacity=0)
        cache.put("a", 1)
        assert cache.get("a") is None


class TestLFUEviction:
    def test_evicts_least_frequent_key(self):
        cache = LFUCache(capacity=2)
        cache.put("a", 1)
        cache.put("b", 2)
        # Access "a" to increase its frequency
        cache.get("a")
        # Insert "c" — should evict "b" (freq=1) not "a" (freq=2)
        cache.put("c", 3)
        assert cache.get("a") == 1
        assert cache.get("b") is None
        assert cache.get("c") == 3

    def test_evicts_oldest_among_same_frequency(self):
        cache = LFUCache(capacity=2)
        cache.put("a", 1)  # older, freq 1
        cache.put("b", 2)  # newer, freq 1
        # Both have freq 1; "a" is older so should be evicted
        cache.put("c", 3)
        assert cache.get("a") is None
        assert cache.get("b") == 2
        assert cache.get("c") == 3

    def test_eviction_chain(self):
        cache = LFUCache(capacity=3)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)
        # Bump "c" frequency
        cache.get("c")
        cache.get("c")
        # Bump "b" frequency
        cache.get("b")
        # Insert "d" — evicts "a" (freq=1, lowest)
        cache.put("d", 4)
        assert cache.get("a") is None
        # Insert "e" — evicts "d" (freq=1, lowest; "b" is 2, "c" is 3)
        cache.put("e", 5)
        assert cache.get("d") is None
        assert cache.get("b") == 2
        assert cache.get("c") == 3


class TestLFUCacheTTL:
    def test_expired_entry_returns_none(self):
        cache = LFUCache(capacity=4, ttl_seconds=1)
        cache.put("a", 1)
        with patch("services.lfu_cache.time") as mock_time:
            # First call for put timestamp, second for get check
            mock_time.time.return_value = time.time() + 2
            assert cache.get("a") is None

    def test_non_expired_entry_returns_value(self):
        cache = LFUCache(capacity=4, ttl_seconds=10)
        cache.put("a", 1)
        assert cache.get("a") == 1


class TestLFUCacheStats:
    def test_stats_initial(self):
        cache = LFUCache(capacity=4)
        stats = cache.stats()
        assert stats["size"] == 0
        assert stats["hits"] == 0
        assert stats["misses"] == 0
        assert stats["hit_rate"] == 0

    def test_stats_after_operations(self):
        cache = LFUCache(capacity=4)
        cache.put("a", 1)
        cache.get("a")     # hit
        cache.get("a")     # hit
        cache.get("miss")  # miss
        stats = cache.stats()
        assert stats["size"] == 1
        assert stats["hits"] == 2
        assert stats["misses"] == 1
        assert stats["hit_rate"] == round(2 / 3, 3)
