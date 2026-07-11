from datetime import datetime

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from sqlalchemy.exc import SQLAlchemyError

from jwt.exceptions import InvalidTokenError


def error_response(
    status_code: int,
    message: str,
    request: Request,
):
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "status": status_code,
            "message": message,
            "path": request.url.path,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


def register_exception_handlers(app: FastAPI):

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request,
        exc: HTTPException,
    ):
        return error_response(
            exc.status_code,
            exc.detail,
            request,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ):
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "status": 422,
                "message": "Validation Error",
                "errors": exc.errors(),
                "path": request.url.path,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(
        request: Request,
        exc: SQLAlchemyError,
    ):
        return error_response(
            500,
            "Database Error",
            request,
        )

    @app.exception_handler(InvalidTokenError)
    async def jwt_exception_handler(
        request: Request,
        exc: InvalidTokenError,
    ):
        return error_response(
            401,
            "Invalid or expired token",
            request,
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(
        request: Request,
        exc: Exception,
    ):
        return error_response(
            500,
            "Internal Server Error",
            request,
        )