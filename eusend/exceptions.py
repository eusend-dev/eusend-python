"""Eusend exceptions.

Mirrors the structure of resend-python's ``resend.exceptions``: a base
``EusendError`` plus specific subclasses, an ``ERRORS`` mapping, and a
``raise_for_code_and_type`` dispatcher. Errors are keyed by the API's stable
``code`` string (e.g. ``"MONTHLY_LIMIT_EXCEEDED"``) rather than by HTTP status.
"""

from typing import Dict, NoReturn, Optional, Type, Union


class EusendError(Exception):
    """Base class for all errors raised by the Eusend SDK.

    Catch this to handle any Eusend failure, and inspect ``code`` to branch on
    the specific cause.

    Attributes:
        message: Human-readable description.
        code: Stable machine-readable code, e.g. ``"MONTHLY_LIMIT_EXCEEDED"``.
        status_code: HTTP status, or ``None`` for a client/network-level error.
        suggested_action: A hint on how to resolve the error.
        headers: Response headers, when available.
    """

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: Optional[int] = None,
        suggested_action: str = "",
        headers: Optional[Dict[str, str]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.suggested_action = suggested_action
        self.headers = headers or {}


class MissingApiKeyError(EusendError):
    """Raised client-side when no API key has been configured."""

    def __init__(
        self,
        message: str = "Missing API key.",
        code: str = "UNAUTHORIZED",
        status_code: Optional[int] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        super().__init__(
            message=message,
            code=code,
            status_code=status_code,
            suggested_action="Set eusend.api_key or the EUSEND_API_KEY environment variable.",
            headers=headers,
        )


class InvalidApiKeyError(EusendError):
    """Raised when the API rejects the API key (401)."""

    def __init__(self, message, code, status_code=None, headers=None):
        super().__init__(
            message=message,
            code=code,
            status_code=status_code,
            suggested_action="Generate a new API key in the dashboard.",
            headers=headers,
        )


class ValidationError(EusendError):
    """Raised for an invalid or malformed request (400)."""

    def __init__(self, message, code, status_code=None, headers=None):
        super().__init__(
            message=message,
            code=code,
            status_code=status_code,
            suggested_action="Check the error message for the offending field.",
            headers=headers,
        )


class NotFoundError(EusendError):
    """Raised when the requested resource does not exist (404)."""

    def __init__(self, message, code, status_code=None, headers=None):
        super().__init__(message=message, code=code, status_code=status_code, headers=headers)


class RateLimitError(EusendError):
    """Raised when a rate limit or send quota is exceeded (429)."""

    def __init__(self, message, code, status_code=None, headers=None):
        super().__init__(
            message=message,
            code=code,
            status_code=status_code,
            suggested_action="Reduce your request rate or wait before retrying.",
            headers=headers,
        )


class ApplicationError(EusendError):
    """Raised for a server error, or a network failure that never reached the server."""

    def __init__(self, message, code="INTERNAL_ERROR", status_code=None, headers=None):
        super().__init__(
            message=message,
            code=code,
            status_code=status_code,
            suggested_action="Please try again; contact support if it persists.",
            headers=headers,
        )


class NoContentError(EusendError):
    """Raised when a body was expected but the API returned no content."""

    def __init__(self) -> None:
        super().__init__(message="No content was returned from the API.", code="INTERNAL_ERROR")


# Maps the API's `code` string to the exception class to raise.
ERRORS: Dict[str, Type[EusendError]] = {
    "UNAUTHORIZED": InvalidApiKeyError,
    "FORBIDDEN": EusendError,
    "NOT_FOUND": NotFoundError,
    "VALIDATION_ERROR": ValidationError,
    "BAD_REQUEST": ValidationError,
    "CONFLICT": EusendError,
    "RATE_LIMITED": RateLimitError,
    "MONTHLY_LIMIT_EXCEEDED": RateLimitError,
    "DAILY_LIMIT_EXCEEDED": RateLimitError,
    "PLAN_LIMIT_EXCEEDED": EusendError,
    "DOMAIN_NOT_VERIFIED": EusendError,
    "SENDING_SUSPENDED": EusendError,
    "ALL_SUPPRESSED": EusendError,
    "ATTACHMENT_STORAGE_ERROR": EusendError,
    "SERVICE_PAUSED": EusendError,
    "INTERNAL_ERROR": ApplicationError,
    "application_error": ApplicationError,
}


def raise_for_code_and_type(
    code: str,
    message: str,
    status_code: Optional[Union[str, int]] = None,
    headers: Optional[Dict[str, str]] = None,
) -> NoReturn:
    """Raise the exception mapped to ``code`` (falling back to ``EusendError``)."""
    exc = ERRORS.get(code, EusendError)
    status = int(status_code) if status_code is not None else None
    raise exc(message=message, code=code, status_code=status, headers=headers)
