"""Custom exception classes and handlers."""

from fastapi import Request
from fastapi.responses import JSONResponse


class AppException(Exception):
    """Base application exception."""

    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail


class NotFoundException(AppException):
    """Resource not found."""

    def __init__(self, resource: str, resource_id: int) -> None:
        super().__init__(404, f"{resource} with id {resource_id} not found")


class ConflictException(AppException):
    """Resource conflict (e.g., duplicate)."""

    def __init__(self, detail: str) -> None:
        super().__init__(409, detail)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Global handler for AppException subclasses."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )
