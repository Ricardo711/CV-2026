from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

#from app.ml.model import load_model
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.mongo import init_mongo, close_mongo
from app.routers.health import router as health_router
from app.routers.predictions import router as predictions_router
from app.routers.auth import router as auth_router
from app.routers.quiz import router as quiz_router
from app.routers.sessions import router as sessions_router
from app.routers.games import router as games_router
from app.routers.images import router as images_router

from app.services.users_service import UsersService


def create_app() -> FastAPI:
    setup_logging(settings.log_level)

    app = FastAPI(title=settings.app_name)

    print("CORS ORIGINS EFFECTIVE:", settings.cors_origins_list)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(predictions_router)
    app.include_router(auth_router)
    app.include_router(quiz_router)
    app.include_router(sessions_router, prefix="/api")
    app.include_router(games_router, prefix="/api")
    app.include_router(images_router, prefix="/api")

    # Static files: /media -> ./media
    media_dir = Path(settings.media_dir)
    media_dir.mkdir(parents=True, exist_ok=True)
    app.mount(
        settings.media_url_prefix,
        StaticFiles(directory=str(media_dir)),
        name="media",
    )

    @app.on_event("startup")
    async def startup() -> None:
        await init_mongo()
        await UsersService.ensure_indexes()

    @app.on_event("shutdown")
    async def shutdown() -> None:
        await close_mongo()

    return app


app = create_app()
