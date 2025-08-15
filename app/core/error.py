from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse

import logging

logger = logging.getLogger(__name__)

def register_exception_handlers(app: FastAPI):

    @app.exception_handlers(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.warning("ValidationError: %s", exc)
        return JSONResponse(status_code=422, content={"detail": exc.errors()})

    @app.exception_handlers(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled error: %s", exc)
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})