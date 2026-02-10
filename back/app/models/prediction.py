from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.models.feedback import PredictionFeedbackOut


class PredictionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    image_url: str
    image_path: str

    predicted_index: int
    predicted_label: str
    confidence: float = Field(ge=0.0, le=1.0)

    student_marbling_answer: str | None = None

    created_at: datetime
    feedback: PredictionFeedbackOut | None = None


class PredictionListOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    image_url: str
    predicted_label: str
    confidence: float

    student_marbling_answer: str | None = None

    created_at: datetime

    feedback: PredictionFeedbackOut | None = None
