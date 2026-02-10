from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException
from app.db.mongo import get_db
from app.models.feedback import PredictionFeedbackIn


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class PredictionsService:
    collection_name = "predictions"

    @staticmethod
    async def create(doc: dict) -> dict:
        db = get_db()
        doc = {**doc, "created_at": _utcnow()}
        res = await db[PredictionsService.collection_name].insert_one(doc)
        return {"id": str(res.inserted_id), **doc}

    @staticmethod
    async def list(limit: int = 50, skip: int = 0) -> list[dict]:
        db = get_db()
        cursor = (
            db[PredictionsService.collection_name]
            .find({})
            .sort("created_at", -1)
            .skip(skip)
            .limit(limit)
        )

        out: list[dict] = []
        async for d in cursor:
            out.append(
                {
                    "id": str(d["_id"]),
                    "image_url": d["image_url"],
                    "predicted_label": d["predicted_label"],
                    "confidence": d["confidence"],
                    "student_marbling_answer": d.get("student_marbling_answer"),
                    "created_at": d["created_at"],
                    "feedback": d.get("feedback"),
                }
            )
        return out

    @staticmethod
    async def get(prediction_id: str) -> dict:
        db = get_db()
        from bson import ObjectId

        try:
            _id = ObjectId(prediction_id)
        except Exception:
            raise HTTPException(status_code=400, detail="id inválido")

        d = await db[PredictionsService.collection_name].find_one({"_id": _id})
        if not d:
            raise HTTPException(status_code=404, detail="Predicción no encontrada")

        return {
            "id": str(d["_id"]),
            "image_url": d["image_url"],
            "image_path": d["image_path"],
            "predicted_index": d["predicted_index"],
            "predicted_label": d["predicted_label"],
            "confidence": d["confidence"],
            "student_marbling_answer": d.get("student_marbling_answer"),
            "created_at": d["created_at"],
            "feedback": d.get("feedback"),
        }

    @staticmethod
    async def delete(prediction_id: str) -> dict:
        db = get_db()
        from bson import ObjectId

        try:
            _id = ObjectId(prediction_id)
        except Exception:
            raise HTTPException(status_code=400, detail="id inválido")

        d = await db[PredictionsService.collection_name].find_one({"_id": _id})
        if not d:
            raise HTTPException(status_code=404, detail="Predicción no encontrada")

        res = await db[PredictionsService.collection_name].delete_one({"_id": _id})
        if res.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Predicción no encontrada")

        # devolvemos lo borrado para que el router pueda borrar el archivo local
        return {
            "id": prediction_id,
            "image_path": d.get("image_path", ""),
            "image_url": d.get("image_url", ""),
        }

    @staticmethod
    async def set_feedback(prediction_id: str, payload: PredictionFeedbackIn) -> dict:
        from app.db.mongo import get_db

        db = get_db()

        from bson import ObjectId

        try:
            _id = ObjectId(prediction_id)
        except Exception:
            raise HTTPException(status_code=400, detail="id inválido")

        feedback_doc = {
            "agree_with_model": payload.agree_with_model,
            "student_confidence": payload.student_confidence,
            "helpfulness_rating": payload.helpfulness_rating,
            "created_at": _utcnow(),
        }

        set_doc: dict = {"feedback": feedback_doc}

        if payload.student_marbling_answer is not None:
            set_doc["student_marbling_answer"] = payload.student_marbling_answer

        res = await db[PredictionsService.collection_name].update_one(
            {"_id": _id},
            {"$set": set_doc},
        )

        if res.matched_count == 0:
            raise HTTPException(status_code=404, detail="Predicción no encontrada")

        return await PredictionsService.get(prediction_id)
