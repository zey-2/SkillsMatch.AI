"""Caching service for SkillsMatch.AI with LRU eviction policy.

This module provides a configurable caching layer for expensive operations
including matching results, search results, and AI analysis.
"""

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Generic, TypeVar, Tuple
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar("T")  # Generic type variable


@dataclass
class CacheEntry(Generic[T]):
    """Single cache entry with metadata."""

    value: T
    created_at: datetime = field(default_factory=datetime.utcnow)
    accessed_at: datetime = field(default_factory=datetime.utcnow)
    ttl_seconds: Optional[float] = None
    access_count: int = 0

    def is_expired(self) -> bool:
        """Check if entry has expired."""
        if self.ttl_seconds is None:
            return False

        elapsed = (datetime.utcnow() - self.created_at).total_seconds()
        return elapsed > self.ttl_seconds

    def touch(self) -> None:
        """Update access time and count."""
        self.accessed_at = datetime.utcnow()
        self.access_count += 1


class LRUCache(Generic[T]):
    """LRU (Least Recently Used) cache with TTL support.

    Features:
    - Configurable maximum size
    - TTL (time-to-live) for entries
    - LRU eviction policy
    - Hit/miss tracking
    - Entry metadata
    """

    def __init__(
        self, max_size: int = 1000, default_ttl_seconds: Optional[float] = None
    ):
        """Initialize LRU cache.

        Args:
            max_size: Maximum number of entries to store
            default_ttl_seconds: Default TTL for entries (None = no expiration)
        """
        self.max_size = max_size
        self.default_ttl_seconds = default_ttl_seconds
        self._cache: Dict[str, CacheEntry[T]] = {}
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Optional[T]:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found or expired
        """
        if key not in self._cache:
            self.misses += 1
            return None

        entry = self._cache[key]

        # Check expiration
        if entry.is_expired():
            del self._cache[key]
            self.misses += 1
            return None

        # Update access info
        entry.touch()
        self.hits += 1

        return entry.value

    def set(self, key: str, value: T, ttl_seconds: Optional[float] = None) -> None:
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Override default TTL for this entry
        """
        # Use provided TTL or fall back to default
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl_seconds

        # Create new entry
        entry = CacheEntry(value=value, ttl_seconds=ttl)
        self._cache[key] = entry

        # Check if we need to evict
        if len(self._cache) > self.max_size:
            self._evict_lru()

    def delete(self, key: str) -> None:
        """Delete entry from cache.

        Args:
            key: Cache key
        """
        if key in self._cache:
            del self._cache[key]

    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
        self.hits = 0
        self.misses = 0

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary with cache stats
        """
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0

        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "total_requests": total_requests,
            "hit_rate_percent": round(hit_rate, 2),
        }

    def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        if not self._cache:
            return

        # Find LRU entry
        lru_key = min(self._cache.keys(), key=lambda k: self._cache[k].accessed_at)

        logger.debug(f"Evicting LRU cache entry: {lru_key}")
        del self._cache[lru_key]


class CacheService:
    """Central caching service for SkillsMatch.AI.

    Manages different cache categories with specific TTL strategies.
    """

    def __init__(self):
        """Initialize cache service with multiple caches."""
        # Different caches for different use cases
        self._matching_cache = LRUCache(
            max_size=500,
            default_ttl_seconds=3600,  # 1 hour
        )
        self._search_cache = LRUCache(
            max_size=200,
            default_ttl_seconds=1800,  # 30 minutes
        )
        self._ai_cache = LRUCache(
            max_size=300,
            default_ttl_seconds=86400,  # 24 hours
        )
        self._skill_cache = LRUCache(
            max_size=100,
            default_ttl_seconds=604800,  # 7 days
        )

    # Matching cache methods
    def get_match_result(self, profile_id: str, job_id: str) -> Optional[Dict]:
        """Get cached matching result.

        Args:
            profile_id: User profile ID
            job_id: Job ID

        Returns:
            Cached match result or None
        """
        key = f"match:{profile_id}:{job_id}"
        return self._matching_cache.get(key)

    def set_match_result(self, profile_id: str, job_id: str, result: Dict) -> None:
        """Cache a matching result.

        Args:
            profile_id: User profile ID
            job_id: Job ID
            result: Match result to cache
        """
        key = f"match:{profile_id}:{job_id}"
        self._matching_cache.set(key, result)
        logger.debug(f"Cached match result: {key}")

    # Search cache methods
    def get_search_result(
        self, search_type: str, query: str, filters_hash: str
    ) -> Optional[Dict]:
        """Get cached search result.

        Args:
            search_type: Type of search (profile, job, etc.)
            query: Search query string
            filters_hash: Hash of applied filters

        Returns:
            Cached search result or None
        """
        key = f"search:{search_type}:{query}:{filters_hash}"
        return self._search_cache.get(key)

    def set_search_result(
        self, search_type: str, query: str, filters_hash: str, result: Dict
    ) -> None:
        """Cache a search result.

        Args:
            search_type: Type of search
            query: Search query string
            filters_hash: Hash of applied filters
            result: Search result to cache
        """
        key = f"search:{search_type}:{query}:{filters_hash}"
        self._search_cache.set(key, result)
        logger.debug(f"Cached search result: {key}")

    # AI analysis cache methods
    def get_ai_analysis(self, profile_id: str, analysis_type: str) -> Optional[Dict]:
        """Get cached AI analysis result.

        Args:
            profile_id: User profile ID
            analysis_type: Type of analysis (summary, skills_gap, etc.)

        Returns:
            Cached analysis result or None
        """
        key = f"ai_analysis:{profile_id}:{analysis_type}"
        return self._ai_cache.get(key)

    def set_ai_analysis(
        self, profile_id: str, analysis_type: str, result: Dict
    ) -> None:
        """Cache an AI analysis result.

        Args:
            profile_id: User profile ID
            analysis_type: Type of analysis
            result: Analysis result to cache
        """
        key = f"ai_analysis:{profile_id}:{analysis_type}"
        self._ai_cache.set(key, result)
        logger.debug(f"Cached AI analysis: {key}")

    # Skill cache methods
    def get_skill_data(self, skill_name: str) -> Optional[Dict]:
        """Get cached skill data.

        Args:
            skill_name: Name of the skill

        Returns:
            Cached skill data or None
        """
        key = f"skill:{skill_name.lower()}"
        return self._skill_cache.get(key)

    def set_skill_data(self, skill_name: str, data: Dict) -> None:
        """Cache skill data.

        Args:
            skill_name: Name of the skill
            data: Skill data to cache
        """
        key = f"skill:{skill_name.lower()}"
        self._skill_cache.set(key, data)
        logger.debug(f"Cached skill data: {key}")

    # Cache invalidation methods
    def invalidate_profile_cache(self, profile_id: str) -> None:
        """Invalidate all caches for a profile.

        Args:
            profile_id: User profile ID
        """
        # Invalidate matching cache entries for this profile
        keys_to_delete = [
            key
            for key in self._matching_cache._cache.keys()
            if key.startswith(f"match:{profile_id}:")
        ]
        for key in keys_to_delete:
            self._matching_cache.delete(key)

        # Invalidate AI analysis caches
        ai_keys = [
            key
            for key in self._ai_cache._cache.keys()
            if key.startswith(f"ai_analysis:{profile_id}:")
        ]
        for key in ai_keys:
            self._ai_cache.delete(key)

        logger.info(f"Invalidated cache for profile: {profile_id}")

    def invalidate_job_cache(self, job_id: str) -> None:
        """Invalidate all caches for a job.

        Args:
            job_id: Job ID
        """
        # Invalidate matching cache entries for this job
        keys_to_delete = [
            key for key in self._matching_cache._cache.keys() if f":{job_id}" in key
        ]
        for key in keys_to_delete:
            self._matching_cache.delete(key)

        logger.info(f"Invalidated cache for job: {job_id}")

    def invalidate_search_cache(self, search_type: Optional[str] = None) -> None:
        """Invalidate search cache.

        Args:
            search_type: Optional search type to invalidate (all if None)
        """
        if search_type is None:
            self._search_cache.clear()
            logger.info("Cleared all search cache")
        else:
            keys_to_delete = [
                key
                for key in self._search_cache._cache.keys()
                if key.startswith(f"search:{search_type}:")
            ]
            for key in keys_to_delete:
                self._search_cache.delete(key)
            logger.info(f"Cleared {search_type} search cache")

    # Statistics methods
    def get_cache_stats(self) -> Dict[str, Dict]:
        """Get statistics for all caches.

        Returns:
            Dictionary with stats for each cache
        """
        return {
            "matching": self._matching_cache.get_stats(),
            "search": self._search_cache.get_stats(),
            "ai_analysis": self._ai_cache.get_stats(),
            "skills": self._skill_cache.get_stats(),
        }

    def print_stats(self) -> None:
        """Print cache statistics to console."""
        stats = self.get_cache_stats()

        print("\n" + "=" * 80)
        print("CACHE SERVICE STATISTICS")
        print("=" * 80)

        for cache_name, cache_stats in stats.items():
            print(f"\n{cache_name.upper()} CACHE:")
            print(f"  Size: {cache_stats['size']}/{cache_stats['max_size']}")
            print(f"  Hits: {cache_stats['hits']}")
            print(f"  Misses: {cache_stats['misses']}")
            print(f"  Hit Rate: {cache_stats['hit_rate_percent']}%")

        print("\n" + "=" * 80)

    def clear_all(self) -> None:
        """Clear all caches."""
        self._matching_cache.clear()
        self._search_cache.clear()
        self._ai_cache.clear()
        self._skill_cache.clear()
        logger.info("Cleared all caches")


# Global cache service instance
_cache_service: Optional[CacheService] = None


def get_cache_service() -> CacheService:
    """Get or create the global cache service.

    Returns:
        CacheService instance
    """
    global _cache_service

    if _cache_service is None:
        _cache_service = CacheService()
        logger.info("Initialized cache service")

    return _cache_service


def cache_result(
    cache_type: str = "ai", key_builder=None, ttl_seconds: Optional[float] = None
):
    """Decorator to cache function results.

    Args:
        cache_type: Type of cache (ai, matching, search, skill)
        key_builder: Optional function to build cache key
        ttl_seconds: Optional TTL override

    Example:
        @cache_result('ai', key_builder=lambda *args: f"skill:{args[0]}")
        def analyze_skill(skill_name):
            ...
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_service = get_cache_service()

            # Build cache key
            if key_builder:
                key = key_builder(*args, **kwargs)
            else:
                key = f"{func.__name__}:{args}:{kwargs}"

            # Try to get from cache
            cache_map = {
                "ai": cache_service._ai_cache,
                "matching": cache_service._matching_cache,
                "search": cache_service._search_cache,
                "skill": cache_service._skill_cache,
            }

            cache = cache_map.get(cache_type)
            if not cache:
                logger.warning(f"Unknown cache type: {cache_type}")
                return func(*args, **kwargs)

            cached_value = cache.get(key)
            if cached_value is not None:
                logger.debug(f"Cache hit for {func.__name__}: {key}")
                return cached_value

            # Call function and cache result
            result = func(*args, **kwargs)
            cache.set(key, result, ttl_seconds=ttl_seconds)
            return result

        return wrapper

    return decorator
