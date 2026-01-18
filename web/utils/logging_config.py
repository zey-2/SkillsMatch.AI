"""
Centralized logging configuration for SkillsMatch.AI.

Provides:
- Structured logging setup
- Request correlation IDs
- Performance tracking
- Consistent log formatting
- Multiple log handlers (console, file, errors)
"""

import logging
import logging.handlers
import json
import uuid
from typing import Optional, Dict, Any
from datetime import datetime
from contextlib import contextmanager
import os

# Global request context for correlation IDs
_request_context: Dict[str, str] = {}


def get_correlation_id() -> str:
    """Get or create current request correlation ID."""
    if "correlation_id" not in _request_context:
        _request_context["correlation_id"] = str(uuid.uuid4())
    return _request_context["correlation_id"]


def set_correlation_id(correlation_id: str) -> None:
    """Set correlation ID for current request."""
    _request_context["correlation_id"] = correlation_id


@contextmanager
def request_context(correlation_id: Optional[str] = None):
    """Context manager for request-scoped logging."""
    old_context = _request_context.copy()
    try:
        if correlation_id:
            set_correlation_id(correlation_id)
        else:
            _request_context["correlation_id"] = str(uuid.uuid4())
        yield
    finally:
        _request_context.clear()
        _request_context.update(old_context)


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": get_correlation_id(),
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add custom attributes
        if hasattr(record, "correlation_id"):
            log_data["correlation_id"] = record.correlation_id
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "request_path"):
            log_data["request_path"] = record.request_path
        if hasattr(record, "response_time"):
            log_data["response_time_ms"] = record.response_time
        if hasattr(record, "status_code"):
            log_data["status_code"] = record.status_code

        return json.dumps(log_data)


class ConsoleFormatter(logging.Formatter):
    """Human-readable formatter for console output."""

    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
        "RESET": "\033[0m",  # Reset
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format log record for console with colors."""
        color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
        reset = self.COLORS["RESET"]

        # Build correlation ID string
        corr_id = get_correlation_id()[:8]  # First 8 chars

        # Build log message
        log_msg = (
            f"{color}[{record.levelname:8}]{reset} "
            f"[{corr_id}] "
            f"{record.name}: {record.getMessage()}"
        )

        # Add exception if present
        if record.exc_info:
            log_msg += f"\n{self.formatException(record.exc_info)}"

        return log_msg


def setup_logging(
    app_name: str = "skillsmatch",
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    use_json: bool = False,
) -> logging.Logger:
    """
    Configure logging for the application.

    Args:
        app_name: Application name for logger
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for logging (creates handler if provided)
        use_json: If True, use JSON formatting; otherwise use human-readable

    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(app_name)
    logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Determine formatter
    if use_json:
        formatter = StructuredFormatter()
    else:
        formatter = ConsoleFormatter()

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (if log_file provided)
    if log_file:
        os.makedirs(os.path.dirname(log_file) or ".", exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
        )
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(StructuredFormatter())
        logger.addHandler(file_handler)

    # Error file handler
    error_file = log_file.replace(".log", "_error.log") if log_file else None
    if error_file:
        error_handler = logging.handlers.RotatingFileHandler(
            error_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(StructuredFormatter())
        logger.addHandler(error_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get logger instance for a module."""
    return logging.getLogger(name)


class LoggingDecorator:
    """Decorators for logging function execution."""

    @staticmethod
    def log_execution(logger: Optional[logging.Logger] = None):
        """Decorator to log function execution with timing."""

        def decorator(func):
            def wrapper(*args, **kwargs):
                nonlocal logger
                if logger is None:
                    logger = get_logger(func.__module__)

                import time

                start_time = time.time()

                logger.info(
                    f"Executing {func.__name__}",
                    extra={"correlation_id": get_correlation_id()},
                )

                try:
                    result = func(*args, **kwargs)
                    duration = (time.time() - start_time) * 1000  # Convert to ms
                    logger.info(
                        f"Completed {func.__name__} in {duration:.2f}ms",
                        extra={
                            "correlation_id": get_correlation_id(),
                            "response_time": duration,
                        },
                    )
                    return result
                except Exception as e:
                    duration = (time.time() - start_time) * 1000
                    logger.error(
                        f"Error in {func.__name__} after {duration:.2f}ms: {str(e)}",
                        exc_info=True,
                        extra={"correlation_id": get_correlation_id()},
                    )
                    raise

            return wrapper

        return decorator

    @staticmethod
    def log_errors(logger: Optional[logging.Logger] = None):
        """Decorator to log only errors."""

        def decorator(func):
            def wrapper(*args, **kwargs):
                nonlocal logger
                if logger is None:
                    logger = get_logger(func.__module__)

                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.error(
                        f"Error in {func.__name__}: {str(e)}",
                        exc_info=True,
                        extra={"correlation_id": get_correlation_id()},
                    )
                    raise

            return wrapper

        return decorator


# Middleware for Flask applications
def setup_request_logging(app) -> None:
    """Setup request logging middleware for Flask app."""
    from flask import request, g
    import time

    @app.before_request
    def before_request():
        """Setup request logging context."""
        # Generate or get correlation ID from headers
        correlation_id = request.headers.get(
            "X-Correlation-ID",
            str(uuid.uuid4()),
        )
        set_correlation_id(correlation_id)
        g.correlation_id = correlation_id
        g.start_time = time.time()

    @app.after_request
    def after_request(response):
        """Log request completion."""
        if hasattr(g, "start_time"):
            duration = (time.time() - g.start_time) * 1000  # Convert to ms

            logger = get_logger("skillsmatch.http")
            extra = {
                "correlation_id": g.correlation_id,
                "request_path": request.path,
                "response_time": duration,
                "status_code": response.status_code,
            }

            # Log based on status code
            if response.status_code >= 500:
                logger.error(
                    f"{request.method} {request.path} - {response.status_code}",
                    extra=extra,
                )
            elif response.status_code >= 400:
                logger.warning(
                    f"{request.method} {request.path} - {response.status_code}",
                    extra=extra,
                )
            else:
                logger.info(
                    f"{request.method} {request.path} - {response.status_code}",
                    extra=extra,
                )

        return response


# Initialize default logger on module import
_default_logger = setup_logging(
    app_name="skillsmatch",
    log_level=os.getenv("LOG_LEVEL", "INFO"),
)
