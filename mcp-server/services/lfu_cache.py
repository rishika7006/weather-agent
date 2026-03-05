import time
import threading
from collections import defaultdict


class LFUCache:
    """Thread-safe LFU (Least Frequently Used) cache with TTL support."""

    def __init__(self, capacity: int = 128, ttl_seconds: int = 300):
        self.capacity = capacity
        self.ttl = ttl_seconds
        self.cache = {}          # key -> value
        self.timestamps = {}     # key -> insertion time
        self.freq = {}           # key -> access frequency
        self.freq_buckets = defaultdict(set)  # frequency -> set of keys
        self.min_freq = 0
        self.lock = threading.Lock()
        self.hits = 0
        self.misses = 0

    def get(self, key: str):
        with self.lock:
            if key not in self.cache:
                self.misses += 1
                return None

            if time.time() - self.timestamps[key] > self.ttl:
                self._remove(key)
                self.misses += 1
                return None

            self._increase_freq(key)
            self.hits += 1
            return self.cache[key]

    def put(self, key: str, value):
        if self.capacity <= 0:
            return

        with self.lock:
            if key in self.cache:
                self.cache[key] = value
                self.timestamps[key] = time.time()
                self._increase_freq(key)
                return

            if len(self.cache) >= self.capacity:
                self._evict()

            self.cache[key] = value
            self.timestamps[key] = time.time()
            self.freq[key] = 1
            self.freq_buckets[1].add(key)
            self.min_freq = 1

    def _increase_freq(self, key: str):
        f = self.freq[key]
        self.freq_buckets[f].discard(key)
        if not self.freq_buckets[f] and f == self.min_freq:
            self.min_freq += 1
        self.freq[key] = f + 1
        self.freq_buckets[f + 1].add(key)

    def _evict(self):
        bucket = self.freq_buckets[self.min_freq]
        # Evict the oldest entry among least-frequent keys
        evict_key = min(bucket, key=lambda k: self.timestamps[k])
        self._remove(evict_key)

    def _remove(self, key: str):
        f = self.freq[key]
        self.freq_buckets[f].discard(key)
        if not self.freq_buckets[f] and f == self.min_freq:
            self.min_freq += 1
        del self.cache[key]
        del self.timestamps[key]
        del self.freq[key]

    def stats(self) -> dict:
        with self.lock:
            total = self.hits + self.misses
            return {
                "size": len(self.cache),
                "capacity": self.capacity,
                "hits": self.hits,
                "misses": self.misses,
                "hit_rate": round(self.hits / total, 3) if total > 0 else 0,
            }
