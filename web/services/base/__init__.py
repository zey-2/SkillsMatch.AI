"""
Base service class providing common functionality for all services.

Services inherit from this class to get:
- Error handling
- Logging
- Database session management
- Request validation
"""

import logging
from typing import Optional, Dict, Any, List, TypeVar, Generic
from abc import ABC

# Configure logging
logger = logging.getLogger(__name__)

T = TypeVar("T")


class ServiceError(Exception):
    """Base exception for service layer errors."""

    def __init__(
        self, message: str, code: str = "SERVICE_ERROR", status_code: int = 500
    ):
        """
        Initialize service error.

        Args:
            message: Error message
            code: Error code for API responses
            status_code: HTTP status code
        """
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for JSON response."""
        return {
            "error": self.code,
            "message": self.message,
            "status_code": self.status_code,
        }


class ValidationError(ServiceError):
    """Validation error for invalid input data."""

    def __init__(self, message: str):
        super().__init__(message, code="VALIDATION_ERROR", status_code=422)


class NotFoundError(ServiceError):
    """Resource not found error."""

    def __init__(self, resource: str, identifier: Any):
        message = f"{resource} not found: {identifier}"
        super().__init__(message, code="NOT_FOUND", status_code=404)


class AuthorizationError(ServiceError):
    """Authorization error for forbidden access."""

    def __init__(self, message: str = "Access denied"):
        super().__init__(message, code="UNAUTHORIZED", status_code=403)


class BaseService(ABC):
    """
    Base service class providing common functionality.

    All services should inherit from this class to ensure consistent:
    - Error handling
    - Logging
    - Validation
    - Database operations
    """

    def __init__(self):
        """Initialize base service."""
        self.logger = logging.getLogger(self.__class__.__name__)

    def log_info(self, message: str, **kwargs) -> None:
        """Log info message."""
        self.logger.info(message, extra=kwargs)

    def log_warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        self.logger.warning(message, extra=kwargs)

    def log_error(self, message: str, **kwargs) -> None:
        """Log error message."""
        self.logger.error(message, extra=kwargs)

    def validate_required_fields(
        self, data: Dict[str, Any], required_fields: List[str]
    ) -> None:
        """
        Validate that all required fields are present.

        Args:
            data: Data dictionary to validate
            required_fields: List of required field names

        Raises:
            ValidationError: If any required fields are missing
        """
        missing_fields = [
            field for field in required_fields if field not in data or not data[field]
        ]

        if missing_fields:
            raise ValidationError(
                f"Missing required fields: {', '.join(missing_fields)}"
            )

    def validate_field_type(
        self,
        data: Dict[str, Any],
        field: str,
        field_type: type,
        allow_none: bool = False,
    ) -> None:
        """
        Validate that a field has the correct type.

        Args:
            data: Data dictionary
            field: Field name to validate
            field_type: Expected type
            allow_none: Whether None values are allowed

        Raises:
            ValidationError: If type validation fails
        """
        if field not in data:
            return

        value = data[field]

        if value is None:
            if not allow_none:
                raise ValidationError(f"Field '{field}' cannot be None")
            return

        if not isinstance(value, field_type):
            raise ValidationError(
                f"Field '{field}' must be {field_type.__name__}, got {type(value).__name__}"
            )

    def validate_string_length(
        self,
        data: Dict[str, Any],
        field: str,
        min_length: int = 0,
        max_length: int = None,
    ) -> None:
        """
        Validate string field length.

        Args:
            data: Data dictionary
            field: Field name to validate
            min_length: Minimum allowed length
            max_length: Maximum allowed length

        Raises:
            ValidationError: If length validation fails
        """
        if field not in data:
            return

        value = data[field]
        if not isinstance(value, str):
            raise ValidationError(f"Field '{field}' must be a string")

        length = len(value)
        if length < min_length:
            raise ValidationError(
                f"Field '{field}' must be at least {min_length} characters"
            )

        if max_length and length > max_length:
            raise ValidationError(
                f"Field '{field}' must be at most {max_length} characters"
            )

    def validate_in_choices(
        self, data: Dict[str, Any], field: str, allowed_choices: List[Any]
    ) -> None:
        """
        Validate that field value is in allowed choices.

        Args:
            data: Data dictionary
            field: Field name to validate
            allowed_choices: List of allowed values

        Raises:
            ValidationError: If value not in choices
        """
        if field not in data:
            return

        value = data[field]
        if value not in allowed_choices:
            raise ValidationError(
                f"Field '{field}' must be one of: {', '.join(map(str, allowed_choices))}"
            )

    def sanitize_string(self, value: str, max_length: int = None) -> str:
        """
        Sanitize string by stripping whitespace and limiting length.

        Args:
            value: String to sanitize
            max_length: Maximum length after sanitization

        Returns:
            Sanitized string
        """
        if not isinstance(value, str):
            return value

        sanitized = value.strip()

        if max_length:
            sanitized = sanitized[:max_length]

        return sanitized

    def handle_error(self, error: Exception) -> Dict[str, Any]:
        """
        Handle exception and convert to API response.

        Args:
            error: Exception that occurred

        Returns:
            Dictionary with error information
        """
        self.log_error(f"Error: {error}")

        if isinstance(error, ServiceError):
            return error.to_dict()

        return {
            "error": "INTERNAL_ERROR",
            "message": "An internal error occurred",
            "status_code": 500,
        }
