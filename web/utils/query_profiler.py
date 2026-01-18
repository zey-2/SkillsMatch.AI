"""Query profiling utilities for performance monitoring.

This module provides decorators and utilities for profiling database queries
and tracking performance metrics in the SkillsMatch.AI application.
"""

import logging
import time
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, TypeVar

logger = logging.getLogger(__name__)

# Type variable for generic function wrapping
F = TypeVar("F", bound=Callable[..., Any])

# Global query metrics storage
_query_metrics: Dict[str, List[float]] = {}


def profile_query(
    threshold_ms: int = 100, track_result_count: bool = True, name: Optional[str] = None
) -> Callable[[F], F]:
    """Decorator to profile database query execution time.

    Args:
        threshold_ms: Log queries slower than this threshold (milliseconds)
        track_result_count: Track number of results returned
        name: Custom name for the query (defaults to function name)

    Returns:
        Decorated function with profiling enabled

    Example:
        @profile_query(threshold_ms=100, name="get_all_profiles")
        def get_all_profiles():
            return db.session.query(Profile).all()
    """

    def decorator(func: F) -> F:
        query_name = name or func.__name__

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.perf_counter()

            try:
                result = func(*args, **kwargs)
                elapsed_ms = (time.perf_counter() - start_time) * 1000

                # Track result count if result is a list
                result_count = len(result) if isinstance(result, list) else 1

                # Store metrics
                if query_name not in _query_metrics:
                    _query_metrics[query_name] = []
                _query_metrics[query_name].append(elapsed_ms)

                # Log if slow
                if elapsed_ms > threshold_ms:
                    logger.warning(
                        f"SLOW QUERY: {query_name} - {elapsed_ms:.2f}ms "
                        f"(results: {result_count})"
                    )
                else:
                    logger.debug(
                        f"Query: {query_name} - {elapsed_ms:.2f}ms "
                        f"(results: {result_count})"
                    )

                return result

            except Exception as e:
                elapsed_ms = (time.perf_counter() - start_time) * 1000
                logger.error(
                    f"Query ERROR: {query_name} - {elapsed_ms:.2f}ms - {str(e)}"
                )
                raise

        return wrapper  # type: ignore

    return decorator


class PerformanceContext:
    """Context manager for profiling code blocks.

    Example:
        with PerformanceContext("matching_operation"):
            results = matching_service.match_profiles(...)
    """

    def __init__(self, operation_name: str, threshold_ms: float = 0):
        """Initialize performance context.

        Args:
            operation_name: Name of the operation being profiled
            threshold_ms: Only log if operation takes longer than this
        """
        self.operation_name = operation_name
        self.threshold_ms = threshold_ms
        self.start_time: Optional[float] = None
        self.elapsed_ms: float = 0

    def __enter__(self) -> "PerformanceContext":
        """Enter context and start timer."""
        self.start_time = time.perf_counter()
        logger.debug(f"START: {self.operation_name}")
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context and log elapsed time."""
        if self.start_time is None:
            return

        self.elapsed_ms = (time.perf_counter() - self.start_time) * 1000

        if exc_type is not None:
            logger.error(
                f"ERROR in {self.operation_name}: {exc_val} ({self.elapsed_ms:.2f}ms)"
            )
        elif self.elapsed_ms > self.threshold_ms:
            logger.warning(f"SLOW: {self.operation_name} - {self.elapsed_ms:.2f}ms")
        else:
            logger.debug(f"END: {self.operation_name} - {self.elapsed_ms:.2f}ms")

    def get_elapsed_ms(self) -> float:
        """Get elapsed time in milliseconds."""
        return self.elapsed_ms


def get_query_metrics(query_name: Optional[str] = None) -> Dict[str, Any]:
    """Get profiling metrics for queries.

    Args:
        query_name: Specific query name to get metrics for (None for all)

    Returns:
        Dictionary with query metrics
    """
    if query_name is None:
        return _calculate_metrics_for_all()
    else:
        if query_name not in _query_metrics:
            return {"name": query_name, "count": 0, "metrics": "No data"}

        times = _query_metrics[query_name]
        return _calculate_metrics(query_name, times)


def _calculate_metrics(query_name: str, times: List[float]) -> Dict[str, Any]:
    """Calculate metrics for a query."""
    if not times:
        return {"name": query_name, "count": 0}

    return {
        "name": query_name,
        "count": len(times),
        "total_ms": sum(times),
        "avg_ms": sum(times) / len(times),
        "min_ms": min(times),
        "max_ms": max(times),
    }


def _calculate_metrics_for_all() -> Dict[str, Any]:
    """Calculate metrics for all queries."""
    all_metrics = {}
    for query_name, times in _query_metrics.items():
        if times:
            all_metrics[query_name] = _calculate_metrics(query_name, times)

    return all_metrics


def reset_metrics(query_name: Optional[str] = None) -> None:
    """Reset performance metrics.

    Args:
        query_name: Specific query to reset (None for all)
    """
    global _query_metrics

    if query_name is None:
        _query_metrics.clear()
        logger.info("Reset all query metrics")
    else:
        if query_name in _query_metrics:
            del _query_metrics[query_name]
            logger.info(f"Reset metrics for {query_name}")


def print_metrics_summary() -> None:
    """Print a summary of all query metrics."""
    metrics = get_query_metrics()

    if not metrics:
        print("No query metrics recorded")
        return

    print("\n" + "=" * 80)
    print("QUERY PERFORMANCE SUMMARY")
    print("=" * 80)

    # Sort by total time
    sorted_metrics = sorted(
        metrics.items(), key=lambda x: x[1].get("total_ms", 0), reverse=True
    )

    for query_name, stats in sorted_metrics:
        if stats.get("count", 0) > 0:
            print(f"\n{query_name}")
            print(f"  Count:    {stats['count']}")
            print(f"  Total:    {stats['total_ms']:.2f}ms")
            print(f"  Average:  {stats['avg_ms']:.2f}ms")
            print(f"  Min:      {stats['min_ms']:.2f}ms")
            print(f"  Max:      {stats['max_ms']:.2f}ms")

    print("\n" + "=" * 80)
