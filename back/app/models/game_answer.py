from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class Game1AnswerIn(BaseModel):
    session_id: str
    round_number: int = Field(ge=1, le=6)
    user_answer: str
    response_time_seconds: float = Field(ge=0)
    confidence: int = Field(ge=1, le=5)


class Game3AnswerIn(BaseModel):
    session_id: str
    round_number: int = Field(ge=1, le=6)
    selected_image_id: str
    response_time_seconds: float = Field(ge=0)


class Game2FinalizeIn(BaseModel):
    final_answer: str
    trust_in_ai: int = Field(ge=1, le=5)
    ai_confidence_rating: int = Field(ge=1, le=5)


class GameAnswerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    session_id: str
    game_type: int
    round_number: int

    image_id: str | None = None

    # Respuestas generales
    user_answer: str | None = None
    correct_answer: str | None = None
    is_correct: bool | None = None
    response_time_seconds: float | None = None

    # Game 1 specific
    confidence: int | None = None

    # Game 3 specific
    correct_image_id: str | None = None
    selected_image_id: str | None = None
    difficulty: str | None = None
    images: list[dict] | None = None

    # Game 2 specific
    first_answer: str | None = None
    first_confidence: int | None = None
    ai_prediction: str | None = None
    ai_confidence: float | None = None
    final_answer: str | None = None
    trust_in_ai: int | None = None
    ai_confidence_rating: int | None = None
    uploaded_image_url: str | None = None
    uploaded_image_path: str | None = None

    created_at: datetime


class RoundSubmitResult(BaseModel):
    answer: GameAnswerOut
    session_score: int
    is_session_complete: bool