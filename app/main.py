from fastapi import FastAPI
from app.core.settings import settings
from app.core.logging import setup_logging
from app.core.errors import register_exception_handlers
from app.api.v1.gst import router as gst_router
from app.api.v1.invoices import router as invoices_router

def create_app() -> FastAPI:
    setup_logging()
    app = FastAPI(title="GST Utils", debug=settings.DEBUG)
    register_exception_handlers(app)
    app.include_router(gst_router, prefix=settings.API_V1_PREFIX)
    app.include_router(invoices_router, prefix=settings.API_V1_PREFIX)
    return app

app = create_app()
