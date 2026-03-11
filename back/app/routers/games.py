from __future__ import annotations

import random

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
#from PIL import Image

from app.core.auth_deps import get_current_user
from app.core.config import settings
from app.core.constants import FOUR_CLASSES, NINE_CLASSES, ROUND_SEQUENCE
#from app.core.ml import predict_pil_image
from app.core.ml_client import predict_with_ml_service
from app.core.cloudinary_storage import upload_image
from app.core.storage import save_upload_to_media, delete_media_by_rel_path
from app.models.game_answer import (
    Game1AnswerIn,
    Game2FinalizeIn,
    Game3AnswerIn,
    GameAnswerOut,
    RoundSubmitResult,
)
from app.services.game_answers_service import GameAnswersService
from app.services.game_images_service import GameImagesService
from app.services.game_sessions_service import GameSessionsService

router = APIRouter(prefix="/games", tags=["games"])

# ── Helpers ──────────────────────────────────────────────────────────────────


def _game_type_for_round(round_number: int) -> int:
    return ROUND_SEQUENCE[round_number - 1]


async def _get_verified_session(session_id: str, student_id: str) -> dict:
    session = await GameSessionsService.get(session_id)
    if session["student_id"] != student_id:
        raise HTTPException(status_code=403, detail="Acceso denegado")
    return session


def _build_placeholder_game1() -> dict:
    marbling_class = random.choice(NINE_CLASSES)
    return {
        "game_type": 1,
        "image": {"id": "placeholder", "image_url": ""},
        "marbling_class_for_answer": marbling_class,
        "correct_answer": marbling_class,
    }


def _build_placeholder_game3() -> dict:
    target_class = random.choice(NINE_CLASSES)
    images = [
        {"id": "placeholder-correct", "image_url": ""},
        {"id": "placeholder-wrong-1", "image_url": ""},
        {"id": "placeholder-wrong-2", "image_url": ""},
    ]
    random.shuffle(images)
    return {
        "game_type": 3,
        "target_class": target_class,
        "correct_image_id": "placeholder-correct",
        "images": images,
    }


# ── Round data ────────────────────────────────────────────────────────────────

@router.get("/round-data")
async def get_round_data(
    session_id: str = Query(...),
    round: int = Query(..., ge=1, le=6),
    current_user: dict = Depends(get_current_user),
) -> dict:
    """
    Retorna los datos de imagen(es) para la ronda indicada.
    Si ya existe un game_answer para esa ronda, retorna el mismo (idempotente).
    No expone la respuesta correcta al cliente.
    """
    #session = await _get_verified_session(session_id, current_user["id"])
    await _get_verified_session(session_id, current_user["id"])
    game_type = _game_type_for_round(round)

    # Verificar si ya existe un answer para esta ronda
    existing = await GameAnswersService.get_by_session_round(session_id, round)
    if existing:
        answer_id = existing["id"]
        return _build_round_response(game_type, answer_id, existing)

    # Crear nuevo game_answer según el tipo de juego
    if game_type == 1:
        #img = await GameImagesService.get_random_for_game1()
        img = await GameImagesService.get_random_for_game1(session_id)
        if img:
            answer_doc = {
                "session_id": session_id,
                "round_number": round,
                "game_type": 1,
                "image_id": img["id"],
                #"correct_answer": img["marbling_class"],
                "correct_answer": img["true_class"],
            }
            created = await GameAnswersService.create(answer_doc)
            return {
                "game_type": 1,
                "answer_id": created["id"],
                "image": {"id": img["id"], "image_url": img["image_url"]},
            }
        else:
            placeholder = _build_placeholder_game1()
            answer_doc = {
                "session_id": session_id,
                "round_number": round,
                "game_type": 1,
                "image_id": "placeholder",
                "correct_answer": placeholder["correct_answer"],
            }
            created = await GameAnswersService.create(answer_doc)
            placeholder["answer_id"] = created["id"]
            del placeholder["marbling_class_for_answer"]
            del placeholder["correct_answer"]
            return placeholder

    elif game_type == 2:
        answer_doc = {
            "session_id": session_id,
            "round_number": round,
            "game_type": 2,
        }
        created = await GameAnswersService.create(answer_doc)
        return {"game_type": 2, "answer_id": created["id"]}

    else:  # game_type == 3
        #game3_data = await GameImagesService.get_images_for_game3()
        game3_data = await GameImagesService.get_images_for_game3(session_id)
        if game3_data:
            answer_doc = {
                "session_id": session_id,
                "round_number": round,
                "game_type": 3,
                "correct_image_id": game3_data["correct_image_id"],
                "correct_answer": game3_data["target_class"],
                "difficulty": game3_data["difficulty"],
                "images": game3_data["images"],
            }
            created = await GameAnswersService.create(answer_doc)
            return {
                "game_type": 3,
                "answer_id": created["id"],
                "target_class": game3_data["target_class"],
                "correct_image_id": game3_data["correct_image_id"],
                "difficulty": game3_data["difficulty"],
                "images": game3_data["images"],
            }
        else:
            placeholder = _build_placeholder_game3()
            answer_doc = {
                "session_id": session_id,
                "round_number": round,
                "game_type": 3,
                "correct_image_id": placeholder["correct_image_id"],
                "correct_answer": placeholder["target_class"],
                "difficulty": "medium",
                "images": placeholder["images"],
            }
            created = await GameAnswersService.create(answer_doc)
            placeholder["answer_id"] = created["id"]
            return placeholder


def _build_round_response(game_type: int, answer_id: str, existing: dict) -> dict:
    """Reconstruye la respuesta de round-data a partir de un answer existente."""
    if game_type == 1:
        return {
            "game_type": 1,
            "answer_id": answer_id,
            "image": {"id": existing.get("image_id", ""), "image_url": ""},
        }
    elif game_type == 2:
        return {"game_type": 2, "answer_id": answer_id}
    else:
        return {
            "game_type": 3,
            "answer_id": answer_id,
            "target_class": existing.get("correct_answer", ""),
            "correct_image_id": existing.get("correct_image_id", ""),
            "difficulty": existing.get("difficulty", "medium"),
            "images": existing.get("images", []),
        }


# ── Submit answers ────────────────────────────────────────────────────────────


@router.post(
    "/answers/game1", response_model=RoundSubmitResult, status_code=status.HTTP_200_OK
)
async def submit_game1(
    payload: Game1AnswerIn,
    current_user: dict = Depends(get_current_user),
) -> RoundSubmitResult:
    """Registra la respuesta del Juego 1 (clasificación de imagen)."""
    await _get_verified_session(payload.session_id, current_user["id"])

    existing = await GameAnswersService.get_by_session_round(
        payload.session_id, payload.round_number
    )
    if not existing:
        raise HTTPException(status_code=404, detail="Datos de ronda no inicializados")
    if existing.get("user_answer") is not None:
        raise HTTPException(status_code=409, detail="Esta ronda ya fue respondida")

    answer = await GameAnswersService.update_game1(
        answer_id=existing["id"],
        user_answer=payload.user_answer,
        response_time_seconds=payload.response_time_seconds,
        confidence=payload.confidence,
    )

    if answer["is_correct"]:
        await GameSessionsService.increment_score(payload.session_id)

    session = await GameSessionsService.advance_round(payload.session_id)

    return {
        "answer": answer,
        "session_score": session["total_score"],
        "is_session_complete": session["is_complete"],
    }


@router.post(
    "/answers/game3", response_model=RoundSubmitResult, status_code=status.HTTP_200_OK
)
async def submit_game3(
    payload: Game3AnswerIn,
    current_user: dict = Depends(get_current_user),
) -> RoundSubmitResult:
    """Registra la respuesta del Juego 3 (selección de imagen correcta)."""
    await _get_verified_session(payload.session_id, current_user["id"])

    existing = await GameAnswersService.get_by_session_round(
        payload.session_id, payload.round_number
    )
    if not existing:
        raise HTTPException(status_code=404, detail="Datos de ronda no inicializados")
    if existing.get("user_answer") is not None:
        raise HTTPException(status_code=409, detail="Esta ronda ya fue respondida")

    answer = await GameAnswersService.update_game3(
        answer_id=existing["id"],
        selected_image_id=payload.selected_image_id,
        response_time_seconds=payload.response_time_seconds,
    )

    if answer["is_correct"]:
        await GameSessionsService.increment_score(payload.session_id)

    session = await GameSessionsService.advance_round(payload.session_id)

    return {
        "answer": answer,
        "session_score": session["total_score"],
        "is_session_complete": session["is_complete"],
    }


# ── Game 2: predict (step 1) ─────────────────────────────────────────────────
@router.post("/predict", status_code=status.HTTP_200_OK)
async def game2_predict(
    file: UploadFile = File(...),
    session_id: str = Form(...),
    round_number: int = Form(...),
    first_answer: str = Form(...),
    first_confidence: int = Form(...),
    response_time_seconds: float = Form(...),
    current_user: dict = Depends(get_current_user),
) -> dict:
    """
    Juego 2 — Paso 1: recibe imagen + primera respuesta del usuario,
    corre el modelo de IA y retorna la predicción.
    """
    if first_confidence < 1 or first_confidence > 5:
        raise HTTPException(
            status_code=422, detail="first_confidence debe estar entre 1 y 5"
        )
    if first_answer not in FOUR_CLASSES:
        raise HTTPException(
            status_code=422, detail=f"first_answer debe ser uno de {FOUR_CLASSES}"
        )

    await _get_verified_session(session_id, current_user["id"])

    existing = await GameAnswersService.get_by_session_round(session_id, round_number)
    if not existing:
        raise HTTPException(status_code=404, detail="Datos de ronda no inicializados")
    if existing.get("ai_prediction") is not None:
        raise HTTPException(
            status_code=409, detail="Predicción ya realizada para esta ronda"
        )

    # Guardar imagen temporalmente
    saved = await save_upload_to_media(file)

    try:
        # Subir a Cloudinary
        uploaded = upload_image(
            saved["abs_path"],
            folder="cv2026/uploads/game2",
            filename=file.filename,
        )

        image_url = uploaded["secure_url"]

        # Inferencia ML
        pred = await predict_with_ml_service(saved["abs_path"])

        # Actualizar game_answer con datos del paso 1
        answer = await GameAnswersService.update_game2_predict(
            answer_id=existing["id"],
            first_answer=first_answer,
            first_confidence=first_confidence,
            response_time_seconds=response_time_seconds,
            ai_prediction=pred["predicted_label"],
            ai_confidence=pred["confidence"],
            uploaded_image_url=image_url,
            uploaded_image_path=uploaded["public_id"],   # <- aquí cambia
        )

        return {
            "answer_id": answer["id"],
            "ai_prediction": pred["predicted_label"],
            "ai_confidence": pred["confidence"],
            "image_url": image_url,
        }

    finally:
        if saved.get("rel_path"):
            delete_media_by_rel_path(saved["rel_path"])


# ── Game 2: finalize (step 2) ─────────────────────────────────────────────────


@router.patch(
    "/answers/{answer_id}/finalize",
    response_model=RoundSubmitResult,
    status_code=status.HTTP_200_OK,
)
async def game2_finalize(
    answer_id: str,
    payload: Game2FinalizeIn,
    current_user: dict = Depends(get_current_user),
) -> RoundSubmitResult:
    """
    Juego 2 — Paso 2: registra la respuesta final, confianza en IA y
    percepción de confianza del modelo.
    """
    if payload.final_answer not in FOUR_CLASSES:
        raise HTTPException(
            status_code=422, detail=f"final_answer debe ser uno de {FOUR_CLASSES}"
        )

    existing_answer = await GameAnswersService.get(answer_id)

    if existing_answer.get("game_type") != 2:
        raise HTTPException(
            status_code=400, detail="Esta respuesta no corresponde al Juego 2"
        )
    if existing_answer.get("final_answer") is not None:
        raise HTTPException(status_code=409, detail="El paso 2 ya fue completado")
    if existing_answer.get("ai_prediction") is None:
        raise HTTPException(status_code=400, detail="Debe completar el paso 1 primero")

    # Verificar que la sesión pertenece al usuario
    await _get_verified_session(existing_answer["session_id"], current_user["id"])

    answer = await GameAnswersService.update_game2_finalize(
        answer_id=answer_id,
        final_answer=payload.final_answer,
        trust_in_ai=payload.trust_in_ai,
        ai_confidence_rating=payload.ai_confidence_rating,
    )

    session = await GameSessionsService.advance_round(existing_answer["session_id"])

    return {
        "answer": answer,
        "session_score": session["total_score"],
        "is_session_complete": session["is_complete"],
    }
