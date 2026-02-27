from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field, model_validator


class PredictionFeedbackIn(BaseModel):
    agree_with_model: int | None = Field(
        default=None, ge=0, le=1, description="0 = no, 1 = yes"
    )
    student_confidence: int | None = Field(
        default=None, ge=1, le=5, description="1 a 5"
    )
    helpfulness_rating: int | None = Field(
        default=None, ge=1, le=5, description="1 a 5"
    )

    # Q1
    student_marbling_answer: str | None = Field(default=None, max_length=100)

    @model_validator(mode="after")
    def at_least_one_field(self):
        if (
            self.student_marbling_answer is None
            and self.agree_with_model is None
            and self.student_confidence is None
            and self.helpfulness_rating is None
        ):
            raise ValueError("At least one feedback field is required.")
        return self


class PredictionFeedbackOut(BaseModel):
    agree_with_model: int | None = Field(default=None, ge=0, le=1)
    student_confidence: int | None = Field(default=None, ge=1, le=5)
    helpfulness_rating: int | None = Field(default=None, ge=1, le=5)
    student_marbling_answer: str | None = Field(default=None, max_length=100)

    created_at: datetime
    updated_at: datetime | None = None
