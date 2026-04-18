from http import HTTPStatus
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class ApplicationError(Exception):
    status_code = HTTPStatus.BAD_REQUEST
    code = "application_error"

    def __init__(self, message: str, details: dict | None = None) -> None:
        self.message = message
        self.details = details or {}
        super().__init__(message)


class AuthenticationError(ApplicationError):
    status_code = HTTPStatus.UNAUTHORIZED
    code = "authentication_error"


class AuthorizationError(ApplicationError):
    status_code = HTTPStatus.FORBIDDEN
    code = "authorization_error"


class NotFoundError(ApplicationError):
    status_code = HTTPStatus.NOT_FOUND
    code = "not_found"


class ConflictError(ApplicationError):
    status_code = HTTPStatus.CONFLICT
    code = "conflict"


class ValidationError(ApplicationError):
    status_code = HTTPStatus.UNPROCESSABLE_ENTITY
    code = "validation_error"


class RateLimitError(ApplicationError):
    status_code = HTTPStatus.TOO_MANY_REQUESTS
    code = "rate_limit_exceeded"


def error_response(
    status_code: int,
    code: str,
    message: str,
    details: dict | None,
    request_id: str | None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": details or {},
            },
            "meta": {
                "request_id": request_id or str(uuid4()),
            },
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApplicationError)
    async def handle_application_error(
        request: Request, exc: ApplicationError
    ) -> JSONResponse:
        return error_response(
            int(exc.status_code),
            exc.code,
            exc.message,
            exc.details,
            getattr(request.state, "request_id", None),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        return error_response(
            int(HTTPStatus.INTERNAL_SERVER_ERROR),
            "internal_server_error",
            "An unexpected error occurred",
            {"exception_type": exc.__class__.__name__}
            if app.debug
            else None,
            getattr(request.state, "request_id", None),
        )
