"""Performance logging utilities for tracking operation metrics.

This module provides utilities for tracking and logging performance metrics
across the SkillsMatch.AI application, including API endpoints and services.
"""

import json
import logging
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, TypeVar

logger = logging.getLogger(__name__)

# Type variable for generic function wrapping
F = TypeVar("F")


@dataclass
class PerformanceMetric:
    """Data class for recording a single performance metric."""

    operation: str
    elapsed_ms: float
    timestamp: str
    endpoint: Optional[str] = None
    status: str = "success"
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert metric to dictionary."""
        return asdict(self)


class PerformanceLogger:
    """Logger for tracking application performance metrics."""

    def __init__(self, log_file: Optional[Path] = None, max_metrics: int = 1000):
        """Initialize performance logger.

        Args:
            log_file: Optional file path to write metrics to
            max_metrics: Maximum metrics to keep in memory (FIFO eviction)
        """
        self.log_file = log_file
        self.max_metrics = max_metrics
        self.metrics: List[PerformanceMetric] = []

    def log_metric(
        self,
        operation: str,
        elapsed_ms: float,
        endpoint: Optional[str] = None,
        status: str = "success",
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log a performance metric.

        Args:
            operation: Operation name being tracked
            elapsed_ms: Execution time in milliseconds
            endpoint: Optional API endpoint
            status: Operation status (success/error/timeout)
            error_message: Optional error description
            metadata: Optional additional data
        """
        metric = PerformanceMetric(
            operation=operation,
            elapsed_ms=elapsed_ms,
            timestamp=datetime.utcnow().isoformat(),
            endpoint=endpoint,
            status=status,
            error_message=error_message,
            metadata=metadata,
        )

        self.metrics.append(metric)

        # Keep metrics list size manageable (FIFO eviction)
        if len(self.metrics) > self.max_metrics:
            self.metrics = self.metrics[-self.max_metrics :]

        # Log warning if operation is slow (>1 second)
        if elapsed_ms > 1000:
            logger.warning(
                f"SLOW OPERATION: {operation} - {elapsed_ms:.2f}ms "
                f"(endpoint: {endpoint})"
            )

        # Write to file if configured
        if self.log_file:
            self._write_metric_to_file(metric)

    def get_metrics_summary(
        self, operation_filter: Optional[str] = None, limit: int = 100
    ) -> Dict[str, Any]:
        """Get summary of recorded metrics.

        Args:
            operation_filter: Filter metrics by operation name
            limit: Maximum metrics to return

        Returns:
            Dictionary with summary statistics
        """
        # Filter metrics if needed
        filtered = self.metrics
        if operation_filter:
            filtered = [
                m
                for m in self.metrics
                if operation_filter.lower() in m.operation.lower()
            ]

        # Get recent metrics (up to limit)
        recent = filtered[-limit:] if limit else filtered

        if not recent:
            return {"count": 0, "metrics": []}

        # Calculate statistics
        times = [m.elapsed_ms for m in recent]
        operations = [m.operation for m in recent]

        return {
            "count": len(recent),
            "total_ms": sum(times),
            "avg_ms": sum(times) / len(times),
            "min_ms": min(times),
            "max_ms": max(times),
            "operations": list(set(operations)),
            "metrics": [m.to_dict() for m in recent],
        }

    def get_operation_stats(self, operation: str) -> Dict[str, Any]:
        """Get statistics for a specific operation.

        Args:
            operation: Operation name to analyze

        Returns:
            Dictionary with operation statistics
        """
        operation_metrics = [m for m in self.metrics if m.operation == operation]

        if not operation_metrics:
            return {"operation": operation, "count": 0}

        times = [m.elapsed_ms for m in operation_metrics]

        return {
            "operation": operation,
            "count": len(operation_metrics),
            "total_ms": sum(times),
            "avg_ms": sum(times) / len(times),
            "min_ms": min(times),
            "max_ms": max(times),
            "success_count": sum(1 for m in operation_metrics if m.status == "success"),
            "error_count": sum(1 for m in operation_metrics if m.status == "error"),
        }

    def get_slowest_operations(self, limit: int = 10) -> List[PerformanceMetric]:
        """Get slowest operations recorded.

        Args:
            limit: Number of operations to return

        Returns:
            List of slowest operations
        """
        sorted_metrics = sorted(self.metrics, key=lambda m: m.elapsed_ms, reverse=True)
        return sorted_metrics[:limit]

    def get_failed_operations(self) -> List[PerformanceMetric]:
        """Get operations that failed.

        Returns:
            List of failed operations
        """
        return [m for m in self.metrics if m.status != "success"]

    def _write_metric_to_file(self, metric: PerformanceMetric) -> None:
        """Write metric to log file.

        Args:
            metric: Metric to write
        """
        try:
            if not self.log_file:
                return

            # Create parent directories if needed
            self.log_file.parent.mkdir(parents=True, exist_ok=True)

            # Append metric as JSON line
            with open(self.log_file, "a") as f:
                f.write(json.dumps(metric.to_dict()) + "\n")

        except Exception as e:
            logger.error(f"Failed to write metric to file: {e}")

    def clear(self) -> None:
        """Clear all recorded metrics."""
        self.metrics.clear()

    def print_summary(self) -> None:
        """Print summary of metrics to console."""
        if not self.metrics:
            print("No metrics recorded")
            return

        summary = self.get_metrics_summary()

        print("\n" + "=" * 80)
        print("PERFORMANCE METRICS SUMMARY")
        print("=" * 80)
        print(f"Total Operations: {summary['count']}")
        print(f"Total Time: {summary['total_ms']:.2f}ms")
        print(f"Average Time: {summary['avg_ms']:.2f}ms")
        print(f"Min Time: {summary['min_ms']:.2f}ms")
        print(f"Max Time: {summary['max_ms']:.2f}ms")
        print(f"Unique Operations: {len(summary['operations'])}")
        print("=" * 80)

        # Print per-operation statistics
        print("\nPER-OPERATION STATISTICS:")
        for operation in summary["operations"]:
            stats = self.get_operation_stats(operation)
            print(f"\n{operation}")
            print(f"  Count:    {stats['count']}")
            print(f"  Average:  {stats['avg_ms']:.2f}ms")
            print(f"  Min:      {stats['min_ms']:.2f}ms")
            print(f"  Max:      {stats['max_ms']:.2f}ms")
            print(f"  Success:  {stats['success_count']}")
            print(f"  Errors:   {stats['error_count']}")

        # Print slowest operations
        slowest = self.get_slowest_operations(5)
        if slowest:
            print("\nSLOWEST OPERATIONS (Top 5):")
            for i, metric in enumerate(slowest, 1):
                print(
                    f"{i}. {metric.operation}: {metric.elapsed_ms:.2f}ms "
                    f"({metric.timestamp})"
                )

        # Print failed operations
        failed = self.get_failed_operations()
        if failed:
            print(f"\nFAILED OPERATIONS: {len(failed)}")
            for metric in failed[:5]:
                print(
                    f"- {metric.operation}: {metric.error_message} ({metric.timestamp})"
                )

        print("\n" + "=" * 80)


# Global performance logger instance
_perf_logger: Optional[PerformanceLogger] = None


def get_performance_logger() -> PerformanceLogger:
    """Get or create the global performance logger.

    Returns:
        PerformanceLogger instance
    """
    global _perf_logger

    if _perf_logger is None:
        _perf_logger = PerformanceLogger()

    return _perf_logger


def init_performance_logger(log_file: Optional[Path] = None) -> PerformanceLogger:
    """Initialize the performance logger.

    Args:
        log_file: Optional file path for metrics

    Returns:
        PerformanceLogger instance
    """
    global _perf_logger

    _perf_logger = PerformanceLogger(log_file=log_file)
    return _perf_logger


def log_performance(
    operation: str,
    elapsed_ms: float,
    endpoint: Optional[str] = None,
    status: str = "success",
    error_message: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """Log a performance metric to the global logger.

    Args:
        operation: Operation name
        elapsed_ms: Execution time in milliseconds
        endpoint: Optional API endpoint
        status: Operation status
        error_message: Optional error message
        metadata: Optional metadata
    """
    logger_instance = get_performance_logger()
    logger_instance.log_metric(
        operation=operation,
        elapsed_ms=elapsed_ms,
        endpoint=endpoint,
        status=status,
        error_message=error_message,
        metadata=metadata,
    )
