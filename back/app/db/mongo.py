from __future__ import annotations

import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import settings

logger = logging.getLogger(__name__)

_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None


def get_db() -> AsyncIOMotorDatabase:
    if _db is None:
        raise RuntimeError("MongoDB no inicializado. Llama init_mongo() en startup.")
    return _db


async def init_mongo() -> None:
    global _client, _db
    _client = AsyncIOMotorClient(settings.mongodb_uri)
    _db = _client[settings.mongodb_db]
    await _ensure_indexes(_db)
    logger.info("MongoDB conectado a %s/%s", settings.mongodb_uri, settings.mongodb_db)


async def close_mongo() -> None:
    global _client, _db
    if _client is not None:
        _client.close()
    _client = None
    _db = None
    logger.info("MongoDB desconectado")


async def _ensure_indexes(db: AsyncIOMotorDatabase) -> None:
    await db["predictions"].create_index(
        [("created_at", -1)], name="predictions_created_at_desc"
    )
    await db["users"].create_index([("email", 1)], unique=True, name="uniq_user_email")
    await db["quiz_images"].create_index(
        [("meat_quality_class", 1)], name="quiz_images_class_asc"
    )
    # game images
    await db["images"].create_index(
        [("marbling_class", 1)], name="images_marbling_class_asc"
    )
    await db["images"].create_index([("created_at", -1)], name="images_created_at_desc")
    # game sessions
    await db["game_sessions"].create_index(
        [("student_id", 1)], name="game_sessions_student_id_asc"
    )
    await db["game_sessions"].create_index(
        [("student_id", 1), ("is_complete", 1)], name="game_sessions_student_active"
    )
    # game answers
    await db["game_answers"].create_index(
        [("session_id", 1), ("round_number", 1)],
        unique=True,
        name="game_answers_session_round_uniq",
    )
