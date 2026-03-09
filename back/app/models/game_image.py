from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class GameImageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    image_url: str
    marbling_class: str | None  # 9-class: High Prime, Average Choice, etc.
    created_at: datetime


class GameImageAdminIn(BaseModel):
    marbling_class: str  # debe ser uno de NINE_CLASSES
