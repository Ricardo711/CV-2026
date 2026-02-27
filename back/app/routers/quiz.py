from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.auth_deps import get_current_user
from app.core.config import settings
from app.models.quiz import QuizQuestionOut
from app.services.quiz_service import QuizService

router = APIRouter(prefix="/quiz", tags=["quiz"])


@router.get("/question", response_model=QuizQuestionOut)
async def get_quiz_question(
    current_user: dict = Depends(get_current_user),
) -> QuizQuestionOut:
    """
    Retorna una pregunta de quiz con 3 imágenes:
    1 correcta (clase objetivo configurada en QUIZ_TARGET_CLASS) + 2 incorrectas.
    Si la colección quiz_images está vacía, retorna imágenes placeholder.
    """
    result = await QuizService.get_quiz_question(settings.quiz_target_class)
    return result
