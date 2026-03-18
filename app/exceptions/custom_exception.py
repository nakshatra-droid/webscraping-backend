"""
Custom Exceptions

Specific exceptions for the application.
"""

from typing import Optional, Any
from fastapi import status
from app.exceptions.base_exception import APIException


class NotFoundException(APIException):
    """404 Not Found - Resource not found."""

    def __init__(
        self,
        message: str = "Resource not found",
        details: Optional[Any] = None,
    ):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            code="NOT_FOUND",
            message=message,
            details=details,
        )


class ConflictException(APIException):
    """409 Conflict - Resource already exists."""

    def __init__(
        self,
        message: str = "Resource already exists",
        details: Optional[Any] = None,
    ):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            code="CONFLICT",
            message=message,
            details=details,
        )


class ValidationException(APIException):
    """422 Unprocessable Entity - Validation error."""

    def __init__(
        self,
        message: str = "Validation error",
        details: Optional[Any] = None,
    ):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            code="VALIDATION_ERROR",
            message=message,
            details=details,
        )


class UnauthorizedException(APIException):
    """401 Unauthorized - Authentication required."""

    def __init__(
        self,
        message: str = "Unauthorized",
        details: Optional[Any] = None,
    ):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="UNAUTHORIZED",
            message=message,
            details=details,
            headers={"WWW-Authenticate": "Bearer"},
        )


class ForbiddenException(APIException):
    """403 Forbidden - Insufficient privileges."""

    def __init__(
        self,
        message: str = "Forbidden",
        details: Optional[Any] = None,
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            code="FORBIDDEN",
            message=message,
            details=details,
        )


class TokenExpiredException(APIException):
    """401 Unauthorized - Token has expired."""

    def __init__(
        self,
        message: str = "Token has expired",
        details: Optional[Any] = None,
    ):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="TOKEN_EXPIRED",
            message=message,
            details=details,
            headers={"WWW-Authenticate": "Bearer"},
        )
