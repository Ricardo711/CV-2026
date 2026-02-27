from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class QuizImageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    image_url: str
    meat_quality_class: str
    is_correct: bool


class QuizQuestionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    target_class: str
    images: list[QuizImageOut]  # siempre 3 items: 1 correcto + 2 incorrectos
