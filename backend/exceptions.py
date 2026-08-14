"""Custom exceptions for IntelStock."""


class IntelStockException(Exception):
    """Base exception for IntelStock."""

    pass


class ValidationError(IntelStockException):
    """Data validation error."""

    pass


class DataNotFoundError(IntelStockException):
    """Resource not found error."""

    pass


class ServiceError(IntelStockException):
    """Service execution error."""

    pass


class ConfigurationError(IntelStockException):
    """Configuration error."""

    pass


class DatabaseError(IntelStockException):
    """Database operation error."""

    pass


class ExternalServiceError(IntelStockException):
    """External service error (API, LLM, etc)."""

    pass


class RateLimitError(ExternalServiceError):
    """Rate limit exceeded error."""

    pass


class AuthenticationError(IntelStockException):
    """Authentication error."""

    pass
