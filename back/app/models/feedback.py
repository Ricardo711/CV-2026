from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class PredictionFeedbackIn(BaseModel):
    agree_with_model: int = Field(ge=0, le=1, description="0 = no, 1 = yes")
    student_confidence: int = Field(ge=1, le=5, description="1 a 5")
    helpfulness_rating: int = Field(ge=1, le=5, description="1 a 5")

    student_marbling_answer: str | None = Field(default=None, max_length=100)


class PredictionFeedbackOut(PredictionFeedbackIn):
    created_at: datetime
