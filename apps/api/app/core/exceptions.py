from typing import Any

from fastapi import Request, status
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse


class CCTrackError(Exception):
    """Base exception for CC Track API domain errors."""

    def __init__(
        self,
        error_code: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class StatementReconciliationError(CCTrackError):
    """Raised when statement balance fails reconciliation."""

    def __init__(
        self,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            error_code="STATEMENT_RECONCILIATION_FAILED",
            message=message,
            status_code=getattr(status, "HTTP_422_UNPROCESSABLE_CONTENT", 422),
            details=details,
        )


class UnsupportedStatementError(CCTrackError):
    """Raised when bank statement format is not recognized."""

    def __init__(
        self,
        message: str = "Unsupported statement format or unrecognized issuing bank.",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            error_code="UNSUPPORTED_STATEMENT_FORMAT",
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


async def cc_track_exception_handler(request: Request, exc: CCTrackError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": exc.error_code,
            "message": exc.message,
            "details": exc.details,
        },
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    detail = exc.detail
    details: dict[str, Any] = {}
    if isinstance(detail, dict):
        error_code = detail.get("error_code", f"HTTP_{exc.status_code}")
        message = detail.get("message", "An HTTP error occurred.")
        details = detail.get("details", {})
    else:
        error_code = f"HTTP_{exc.status_code}"
        message = str(detail)

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": error_code,
            "message": message,
            "details": details,
        },
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error_code": "REQUEST_VALIDATION_FAILED",
            "message": "The request payload failed schema validation.",
            "details": {"errors": exc.errors()},
        },
    )


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred processing the request.",
            "details": {"error_type": type(exc).__name__},
        },
    )
