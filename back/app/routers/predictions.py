from __future__ import annotations

from fastapi import APIRouter, File, UploadFile, Query, status, Form

#from app.ml.model import predict_image
from app.core.ml_client import predict_with_ml_service
from app.core.cloudinary_storage import upload_image
from app.core.config import settings
from app.core.storage import save_upload_to_media, delete_media_by_rel_path
from app.models.prediction import PredictionOut, PredictionListOut
from app.services.predictions_service import PredictionsService
from app.models.feedback import PredictionFeedbackIn

router = APIRouter(tags=["predictions"])


@router.post(
    "/predict", response_model=PredictionOut, status_code=status.HTTP_201_CREATED
)
async def predict(
    file: UploadFile = File(...),
    student_marbling_answer: str | None = Form(default=None),
):
    # 1) Guardar imagen temporalmente
    saved = await save_upload_to_media(file)

    try:
        # 2) Subir imagen a Cloudinary
        uploaded = upload_image(
            saved["abs_path"],
            folder="cv2026/uploads/predictions",
            filename=file.filename,
        )

        # 3) Inferencia con el servicio ML usando el archivo temporal
        pred = await predict_with_ml_service(saved["abs_path"])

        # 4) Persistir en DB usando Cloudinary
        doc = {
            "image_url": uploaded["secure_url"],
            "image_path": uploaded["public_id"],
            "student_marbling_answer": student_marbling_answer,
            **pred,
        }
        created = await PredictionsService.create(doc)

        return {
            "id": created["id"],
            "image_url": created["image_url"],
            "image_path": created["image_path"],
            "predicted_index": created["predicted_index"],
            "predicted_label": created["predicted_label"],
            "confidence": created["confidence"],
            "created_at": created["created_at"],
            "student_marbling_answer": created["student_marbling_answer"],
        }

    finally:
        if saved.get("rel_path"):
            delete_media_by_rel_path(saved["rel_path"])


@router.get("/predictions", response_model=list[PredictionListOut])
async def list_predictions(
    limit: int = Query(default=50, ge=1, le=200),
    skip: int = Query(default=0, ge=0),
):
    return await PredictionsService.list(limit=limit, skip=skip)


@router.get("/predictions/{prediction_id}", response_model=PredictionOut)
async def get_prediction(prediction_id: str):
    return await PredictionsService.get(prediction_id)


@router.delete("/predictions/{prediction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prediction(prediction_id: str):
    deleted = await PredictionsService.delete(prediction_id)
    if deleted.get("image_path"):
        delete_media_by_rel_path(deleted["image_path"])
        pass
    return None


@router.post("/predictions/{prediction_id}/feedback", response_model=PredictionOut)
async def add_prediction_feedback(prediction_id: str, payload: PredictionFeedbackIn):
    return await PredictionsService.set_feedback(prediction_id, payload)