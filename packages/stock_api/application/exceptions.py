from typing import Any


class ApplicationException(Exception):
    """Base class for application-level exceptions."""

    def __init__(self, message: str, *, payload: Any = None):
        super().__init__(message)
        self.payload = payload


class NotFoundException(ApplicationException):
    """Raised when a requested resource is not found."""

    pass


class BadRequestException(ApplicationException):
    """Raised when the request is invalid."""

    pass
