# app/cache.py
"""
Simple thread-safe in-memory cache for VidyaLoan queries.
Reduces latency and token consumption on repeated queries.
Tracks cache hits, misses, and hit ratio.
"""
import re
import threading
import time
from typing import Any


def normalize_query(query: str) -> str:
    """Normalize query for cache lookup (lowercase, stripped, collapsed whitespace)."""
    q = (query or "").strip().lower()
    return re.sub(r"\s+", " ", q)


class QueryCache:
    """Thread-safe LRU-style cache for RAG responses."""

    def __init__(self, max_size: int = 500, ttl_seconds: float = 86400.0):
        self.max_size = max_size
        self.ttl = ttl_seconds
        self._cache: dict[str, dict[str, Any]] = {}
        self._lock = threading.Lock()
        self._hits = 0
        self._misses = 0

    def get(self, query: str) -> dict[str, Any] | None:
        """Retrieve cached response if present and unexpired."""
        key = normalize_query(query)
        if not key:
            return None

        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                self._misses += 1
                return None

            # Check expiration
            if time.time() - entry["timestamp"] > self.ttl:
                del self._cache[key]
                self._misses += 1
                return None

            self._hits += 1
            entry["hit_count"] += 1
            return dict(entry["response"])

    def set(self, query: str, response: dict[str, Any]) -> None:
        """Store response in cache."""
        key = normalize_query(query)
        if not key:
            return

        with self._lock:
            if len(self._cache) >= self.max_size and key not in self._cache:
                # Evict oldest entry
                oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k]["timestamp"])
                del self._cache[oldest_key]

            self._cache[key] = {
                "response": dict(response),
                "timestamp": time.time(),
                "hit_count": 0,
            }

    def clear(self) -> None:
        """Clear all cached entries."""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0

    def get_stats(self) -> dict[str, Any]:
        """Return cache hit/miss statistics."""
        with self._lock:
            total = self._hits + self._misses
            ratio = round((self._hits / total) * 100.0, 2) if total > 0 else 0.0
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "hits": self._hits,
                "misses": self._misses,
                "total_lookups": total,
                "hit_ratio_pct": ratio,
            }


# Global singleton cache instance
_cache_instance: QueryCache | None = None


def get_query_cache() -> QueryCache:
    """Return singleton QueryCache instance."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = QueryCache()
    return _cache_instance
