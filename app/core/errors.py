from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from fastapi.exceptions import RequestValidationError
import logging

log = logging.getLogger(__name__)

def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_: Request, exc: RequestValidationError):
        return JSONResponse(status_code=422, content={"detail": exc.errors()})

    @app.exception_handler(ValidationError)
    async def pydantic_validation_handler(_: Request, exc: ValidationError):
        return JSONResponse(status_code=422, content={"detail": exc.errors()})

    @app.exception_handler(Exception)
    async def unhandled(_: Request, exc: Exception):
        log.exception("Unhandled error")
        return JSONResponse(status_code=500, content={"detail": "Processing error"})
