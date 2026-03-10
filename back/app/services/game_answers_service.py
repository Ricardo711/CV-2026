from __future__ import annotations

from datetime import datetime, timezone

from bson import ObjectId
from fastapi import HTTPException

from app.db.mongo import get_db

COLLECTION = "game_answers"


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _to_out(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]),
        "session_id": doc["session_id"],
        "game_type": doc["game_type"],
        "round_number": doc["round_number"],
        "image_id": doc.get("image_id"),
        "user_answer": doc.get("user_answer"),
        "correct_answer": doc.get("correct_answer"),
        "is_correct": doc.get("is_correct"),
        "response_time_seconds": doc.get("response_time_seconds"),

        # Game 1 fields
        "confidence": doc.get("confidence"),

        # Game 2 fields
        "first_answer": doc.get("first_answer"),
        "first_confidence": doc.get("first_confidence"),
        "ai_prediction": doc.get("ai_prediction"),
        "ai_confidence": doc.get("ai_confidence"),
        "final_answer": doc.get("final_answer"),
        "trust_in_ai": doc.get("trust_in_ai"),
        "ai_confidence_rating": doc.get("ai_confidence_rating"),
        "uploaded_image_path": doc.get("uploaded_image_path"),
        "uploaded_image_url": doc.get("uploaded_image_url"),
        "created_at": doc["created_at"],
    }


class GameAnswersService:
    @staticmethod
    async def create(doc: dict) -> dict:
        db = get_db()
        doc = {**doc, "created_at": _utcnow()}
        res = await db[COLLECTION].insert_one(doc)
        return {"id": str(res.inserted_id), **doc}

    @staticmethod
    async def get(answer_id: str) -> dict:
        db = get_db()
        try:
            _id = ObjectId(answer_id)
        except Exception:
            raise HTTPException(status_code=400, detail="answer_id inválido")

        doc = await db[COLLECTION].find_one({"_id": _id})
        if not doc:
            raise HTTPException(status_code=404, detail="Respuesta no encontrada")
        return _to_out(doc)

    @staticmethod
    async def get_by_session_round(session_id: str, round_number: int) -> dict | None:
        db = get_db()
        doc = await db[COLLECTION].find_one(
            {"session_id": session_id, "round_number": round_number}
        )
        return _to_out(doc) if doc else None

    @staticmethod
    async def update_game1(
        answer_id: str,
        user_answer: str,
        response_time_seconds: float,
        confidence: int,
    ) -> dict:
        db = get_db()
        try:
            _id = ObjectId(answer_id)
        except Exception:
            raise HTTPException(status_code=400, detail="answer_id inválido")

        doc = await db[COLLECTION].find_one({"_id": _id})
        if not doc:
            raise HTTPException(status_code=404, detail="Respuesta no encontrada")

        is_correct = user_answer == doc.get("correct_answer")

        await db[COLLECTION].update_one(
            {"_id": _id},
            {
                "$set": {
                    "user_answer": user_answer,
                    "is_correct": is_correct,
                    "response_time_seconds": response_time_seconds,
                    "confidence": confidence,
                }
            },
        )

        updated = await db[COLLECTION].find_one({"_id": _id})
        return _to_out(updated)  # type: ignore[arg-type]

    @staticmethod
    async def update_game3(
        answer_id: str,
        selected_image_id: str,
        response_time_seconds: float,
    ) -> dict:
        db = get_db()
        try:
            _id = ObjectId(answer_id)
        except Exception:
            raise HTTPException(status_code=400, detail="answer_id inválido")

        doc = await db[COLLECTION].find_one({"_id": _id})
        if not doc:
            raise HTTPException(status_code=404, detail="Respuesta no encontrada")

        is_correct = selected_image_id == doc.get("correct_image_id")

        await db[COLLECTION].update_one(
            {"_id": _id},
            {
                "$set": {
                    "user_answer": selected_image_id,
                    "is_correct": is_correct,
                    "response_time_seconds": response_time_seconds,
                }
            },
        )

        updated = await db[COLLECTION].find_one({"_id": _id})
        return _to_out(updated)  # type: ignore[arg-type]

    @staticmethod
    async def update_game2_predict(
        answer_id: str,
        first_answer: str,
        first_confidence: int,
        response_time_seconds: float,
        ai_prediction: str,
        ai_confidence: float,
        uploaded_image_url: str,
        uploaded_image_path: str,
    ) -> dict:
        db = get_db()
        try:
            _id = ObjectId(answer_id)
        except Exception:
            raise HTTPException(status_code=400, detail="answer_id inválido")

        await db[COLLECTION].update_one(
            {"_id": _id},
            {
                "$set": {
                    "first_answer": first_answer,
                    "first_confidence": first_confidence,
                    "response_time_seconds": response_time_seconds,
                    "ai_prediction": ai_prediction,
                    "ai_confidence": ai_confidence,
                    "uploaded_image_url": uploaded_image_url,
                    "uploaded_image_path": uploaded_image_path,
                }
            },
        )

        updated = await db[COLLECTION].find_one({"_id": _id})
        return _to_out(updated)  # type: ignore[arg-type]

    @staticmethod
    async def update_game2_finalize(
        answer_id: str,
        final_answer: str,
        trust_in_ai: int,
        ai_confidence_rating: int,
    ) -> dict:
        db = get_db()
        try:
            _id = ObjectId(answer_id)
        except Exception:
            raise HTTPException(status_code=400, detail="answer_id inválido")

        await db[COLLECTION].update_one(
            {"_id": _id},
            {
                "$set": {
                    "final_answer": final_answer,
                    "trust_in_ai": trust_in_ai,
                    "ai_confidence_rating": ai_confidence_rating,
                }
            },
        )

        updated = await db[COLLECTION].find_one({"_id": _id})
        return _to_out(updated)  # type: ignore[arg-type]