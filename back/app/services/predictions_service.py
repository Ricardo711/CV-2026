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
        db = get_db()

        from bson import ObjectId

        try:
            _id = ObjectId(prediction_id)
        except Exception:
            raise HTTPException(status_code=400, detail="id inválido")

        data = payload.model_dump(exclude_none=True)
        now = _utcnow()

        set_doc: dict[str, object] = {f"feedback.{k}": v for k, v in data.items()}
        set_doc["feedback.updated_at"] = now

        if "student_marbling_answer" in data:
            set_doc["student_marbling_answer"] = data["student_marbling_answer"]

        existing = await db[PredictionsService.collection_name].find_one(
            {"_id": _id},
            {"feedback.created_at": 1},
        )
        if not existing:
            raise HTTPException(status_code=404, detail="Predicción no encontrada")

        feedback_created = (existing.get("feedback") or {}).get("created_at")
        if feedback_created is None:
            set_doc["feedback.created_at"] = now

        await db[PredictionsService.collection_name].update_one(
            {"_id": _id},
            {"$set": set_doc},
        )

        return await PredictionsService.get(prediction_id)
