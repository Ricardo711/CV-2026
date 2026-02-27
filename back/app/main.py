from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.logging import setup_logging
from app.db.mongo import init_mongo, close_mongo
from app.routers.health import router as health_router
from app.routers.predictions import router as predictions_router
from app.routers.auth import router as auth_router
from app.routers.quiz import router as quiz_router

def create_app() -> FastAPI:
    setup_logging(settings.log_level)

    app = FastAPI(title=settings.app_name)

    print("CORS ORIGINS EFFECTIVE:", settings.cors_origins_list)  # 👈 aquí

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,  # NO "*"
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(predictions_router)
    app.include_router(auth_router)
    app.include_router(quiz_router)

    # Static files: /media -> ./media
    media_dir = Path(settings.media_dir)
    media_dir.mkdir(parents=True, exist_ok=True)
    app.mount(
        settings.media_url_prefix, StaticFiles(directory=str(media_dir)), name="media"
    )

    @app.on_event("startup")
    async def _startup() -> None:
        await init_mongo()

    @app.on_event("shutdown")
    async def _shutdown() -> None:
        await close_mongo()

    return app


app = create_app()
