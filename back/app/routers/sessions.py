from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.core.auth_deps import get_current_user
from app.models.game_session import GameSessionOut
from app.services.game_sessions_service import GameSessionsService

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=GameSessionOut, status_code=status.HTTP_201_CREATED)
async def create_session(
    current_user: dict = Depends(get_current_user),
) -> GameSessionOut:
    """Crea una nueva sesión de juego de 6 rondas para el estudiante autenticado."""
    session = await GameSessionsService.create(student_id=current_user["id"])
    return session


@router.get("/{session_id}", response_model=GameSessionOut)
async def get_session(
    session_id: str,
    current_user: dict = Depends(get_current_user),
) -> GameSessionOut:
    """Retorna el estado de una sesión de juego."""
    session = await GameSessionsService.get(session_id)
    if session["student_id"] != current_user["id"]:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Acceso denegado")
    return session
