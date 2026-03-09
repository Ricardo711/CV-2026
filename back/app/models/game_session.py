from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class GameSessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    student_id: str
    start_time: datetime
    end_time: datetime | None
    total_score: int
    total_rounds: int
    current_round: int
    is_complete: bool
    round_sequence: list[int]
