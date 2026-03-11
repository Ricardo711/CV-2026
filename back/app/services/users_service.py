from __future__ import annotations

from datetime import datetime, timezone

from bson import ObjectId
from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError

from app.core.security import hash_password, verify_password
from app.db.mongo import get_db


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class UsersService:
    collection_name = "users"

    @staticmethod
    async def ensure_indexes() -> None:
        db = get_db()
        await db[UsersService.collection_name].create_index(
            [("username", 1)],
            unique=True,
            name="uniq_user_username",
            partialFilterExpression={"username": {"$type": "string"}},
        )

    @staticmethod
    async def create_user(
        username: str,
        password: str,
    ) -> dict:
        db = get_db()

        normalized_username = username.strip().lower()

        doc = {
            "username": normalized_username,
            "password_hash": hash_password(password),
            "created_at": _utcnow(),
        }

        try:
            res = await db[UsersService.collection_name].insert_one(doc)
        except DuplicateKeyError as e:
            errmsg = str(e)

            if "username" in errmsg:
                raise HTTPException(
                    status_code=409,
                    detail="Ese username ya está registrado.",
                )

            raise HTTPException(
                status_code=409,
                detail=f"DuplicateKeyError real: {errmsg}",
            )



        return {
            "id": str(res.inserted_id),
            "username": doc["username"],
            "created_at": doc["created_at"],
        }

    @staticmethod
    async def authenticate(username: str, password: str) -> dict:
        db = get_db()

        normalized_username = username.strip().lower()

        user = await db[UsersService.collection_name].find_one(
            {"username": normalized_username}
        )
        if not user:
            raise HTTPException(status_code=401, detail="Credenciales inválidas.")

        if not verify_password(password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Credenciales inválidas.")

        return {
            "id": str(user["_id"]),
            "username": user["username"],
            "created_at": user["created_at"],
        }

    @staticmethod
    async def get_by_id(user_id: str) -> dict:
        db = get_db()

        try:
            _id = ObjectId(user_id)
        except Exception:
            raise HTTPException(status_code=400, detail="id inválido")

        user = await db[UsersService.collection_name].find_one({"_id": _id})
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        return {
            "id": str(user["_id"]),
            "username": user["username"],
            "created_at": user["created_at"],
        }