from __future__ import annotations

from fastapi import FastAPI

from app.api.v1.routes import api_router
from app.core.config import get_settings
from app.core.database import Database
from app.core.exceptions_handler import install_exception_handlers
from app.core.logging import configure_logging
from app.core.openapi import OPENAPI_TAGS, install_openapi


def create_app(*, database_url: str | None = None) -> FastAPI:
    settings = get_settings()
    configure_logging()

    app = FastAPI(
        title=settings.app_name,
        description="Finance management / budget tracker API for the DhanSutra mobile app.",
        version="0.1.0",
        openapi_url="/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_tags=OPENAPI_TAGS,
    )
    install_exception_handlers(app)
    install_openapi(app)

    url = database_url or settings.database_url
    app.state.db = Database.from_url(url)

    app.include_router(api_router, prefix="/api/v1")
    return app
