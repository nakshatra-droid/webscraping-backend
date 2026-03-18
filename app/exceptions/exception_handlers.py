"""
Exception Handlers

Unified error response format for all exceptions.
"""

from fastapi import FastAPI, Request, HTTPException, logger
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.exceptions.base_exception import APIException
import logging

logger = logging.getLogger(__name__)


class ExceptionHandlers:
    @staticmethod
    async def api_exception_handler(
        request: Request, exc: APIException
    ) -> JSONResponse:
        """Handler for all API-specific exceptions."""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": exc.code,
                    "message": exc.detail.get("message", str(exc.detail))
                    if isinstance(exc.detail, dict)
                    else str(exc.detail),
                    "details": exc.detail.get("details", {})
                    if isinstance(exc.detail, dict)
                    else {},
                },
            },
        )

    @staticmethod
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handler for Pydantic validation errors."""
        formatted_errors = {}
        for error in exc.errors():
            field = error["loc"][-1] if error["loc"] else "general"
            formatted_errors.setdefault(str(field), []).append(error["msg"])

        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid input",
                    "details": formatted_errors,
                },
            },
        )

    @staticmethod
    async def http_exception_handler(
        request: Request, exc: HTTPException
    ) -> JSONResponse:
        """Handler for generic HTTP exceptions."""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": "HTTP_ERROR",
                    "message": str(exc.detail),
                    "details": {},
                },
            },
        )

    @staticmethod
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Handler for any unhandled exceptions."""
        logger.exception(f"Unhandled exception: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "Internal server error",
                    "details": None,
                },
            },
        )

    @staticmethod
    def setup_exception_handlers(app: FastAPI) -> None:
        """Register all custom exception handlers to the FastAPI app."""
        app.add_exception_handler(APIException, ExceptionHandlers.api_exception_handler)
        app.add_exception_handler(
            RequestValidationError, ExceptionHandlers.validation_exception_handler
        )
        app.add_exception_handler(
            HTTPException, ExceptionHandlers.http_exception_handler
        )
        app.add_exception_handler(
            Exception, ExceptionHandlers.unhandled_exception_handler
        )
