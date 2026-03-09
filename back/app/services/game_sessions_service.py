from __future__ import annotations

from datetime import datetime, timezone

from bson import ObjectId
from fastapi import HTTPException

from app.core.constants import ROUND_SEQUENCE, TOTAL_ROUNDS
from app.db.mongo import get_db

COLLECTION = "game_sessions"


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _to_out(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]),
        "student_id": doc["student_id"],
        "start_time": doc["start_time"],
        "end_time": doc.get("end_time"),
        "total_score": doc.get("total_score", 0),
        "total_rounds": doc.get("total_rounds", TOTAL_ROUNDS),
        "current_round": doc.get("current_round", 1),
        "is_complete": doc.get("is_complete", False),
        "round_sequence": doc.get("round_sequence", ROUND_SEQUENCE),
    }


class GameSessionsService:
    @staticmethod
    async def create(student_id: str) -> dict:
        db = get_db()
        doc = {
            "student_id": student_id,
            "start_time": _utcnow(),
            "end_time": None,
            "total_score": 0,
            "total_rounds": TOTAL_ROUNDS,
            "current_round": 1,
            "is_complete": False,
            "round_sequence": ROUND_SEQUENCE,
        }
        res = await db[COLLECTION].insert_one(doc)
        return {"id": str(res.inserted_id), **doc}

    @staticmethod
    async def get(session_id: str) -> dict:
        db = get_db()
        try:
            _id = ObjectId(session_id)
        except Exception:
            raise HTTPException(status_code=400, detail="session_id inválido")

        doc = await db[COLLECTION].find_one({"_id": _id})
        if not doc:
            raise HTTPException(status_code=404, detail="Sesión no encontrada")
        return _to_out(doc)

    @staticmethod
    async def get_active(student_id: str) -> dict | None:
        """Retorna la sesión activa (no completada) del estudiante, si existe."""
        db = get_db()
        doc = await db[COLLECTION].find_one(
            {"student_id": student_id, "is_complete": False},
            sort=[("start_time", -1)],
        )
        return _to_out(doc) if doc else None

    @staticmethod
    async def increment_score(session_id: str) -> None:
        db = get_db()
        try:
            _id = ObjectId(session_id)
        except Exception:
            raise HTTPException(status_code=400, detail="session_id inválido")

        await db[COLLECTION].update_one(
            {"_id": _id},
            {"$inc": {"total_score": 1}},
        )

    @staticmethod
    async def advance_round(session_id: str) -> dict:
        """
        Incrementa current_round. Si ya se completaron todas las rondas,
        marca la sesión como completa y guarda end_time.
        Retorna el documento actualizado.
        """
        db = get_db()
        try:
            _id = ObjectId(session_id)
        except Exception:
            raise HTTPException(status_code=400, detail="session_id inválido")

        doc = await db[COLLECTION].find_one({"_id": _id})
        if not doc:
            raise HTTPException(status_code=404, detail="Sesión no encontrada")

        next_round = doc.get("current_round", 1) + 1
        total = doc.get("total_rounds", TOTAL_ROUNDS)

        if next_round > total:
            await db[COLLECTION].update_one(
                {"_id": _id},
                {"$set": {"is_complete": True, "end_time": _utcnow()}},
            )
        else:
            await db[COLLECTION].update_one(
                {"_id": _id},
                {"$set": {"current_round": next_round}},
            )

        updated = await db[COLLECTION].find_one({"_id": _id})
        return _to_out(updated)  # type: ignore[arg-type]
