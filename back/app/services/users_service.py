from __future__ import annotations

from datetime import datetime, timezone

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
            [("email", 1)], unique=True, name="uniq_user_email"
        )

    @staticmethod
    async def create_user(email: str, password: str, full_name: str | None) -> dict:
        db = get_db()
        doc = {
            "email": email.lower(),
            "password_hash": hash_password(password),
            "full_name": full_name,
            "created_at": _utcnow(),
        }
        try:
            res = await db[UsersService.collection_name].insert_one(doc)
        except DuplicateKeyError:
            raise HTTPException(status_code=409, detail="Ese email ya está registrado.")

        return {
            "id": str(res.inserted_id),
            "email": doc["email"],
            "full_name": doc["full_name"],
            "created_at": doc["created_at"],
        }

    @staticmethod
    async def authenticate(email: str, password: str) -> dict:
        db = get_db()
        user = await db[UsersService.collection_name].find_one({"email": email.lower()})
        if not user:
            raise HTTPException(status_code=401, detail="Credenciales inválidas.")

        if not verify_password(password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Credenciales inválidas.")

        return {
            "id": str(user["_id"]),
            "email": user["email"],
            "full_name": user.get("full_name"),
            "created_at": user["created_at"],
        }

    @staticmethod
    async def get_by_id(user_id: str) -> dict:
        db = get_db()
        from bson import ObjectId

        try:
            _id = ObjectId(user_id)
        except Exception:
            raise HTTPException(status_code=400, detail="id inválido")

        user = await db[UsersService.collection_name].find_one({"_id": _id})
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        return {
            "id": str(user["_id"]),
            "email": user["email"],
            "full_name": user.get("full_name"),
            "created_at": user["created_at"],
        }
