from __future__ import annotations

import io
from PIL import Image

from fastapi import APIRouter, File, UploadFile, Query, status, Form

from app.core.config import settings
from app.core.ml import predict_pil_image
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
    # 1) Guardar imagen localmente
    saved = await save_upload_to_media(file)
    # 2) Cargar PIL desde el archivo guardado
    img = Image.open(saved["abs_path"]).convert("RGB")

    # Reduce tamaño para bajar RAM/CPU (ajusta 1024 si quieres)
    img.thumbnail((1024, 1024))
    # 3) Inferencia
    pred = predict_pil_image(img)
    # 4) Construir URL pública servida por StaticFiles
    image_url = settings.build_public_url(saved["rel_path"])
    # 5) Persistir en DB
    doc = {
        "image_url": image_url,
        "image_path": saved["rel_path"],
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
    # Borra archivo local
    if deleted.get("image_path"):
        delete_media_by_rel_path(deleted["image_path"])
    return None


@router.post("/predictions/{prediction_id}/feedback", response_model=PredictionOut)
async def add_prediction_feedback(prediction_id: str, payload: PredictionFeedbackIn):
    return await PredictionsService.set_feedback(prediction_id, payload)
