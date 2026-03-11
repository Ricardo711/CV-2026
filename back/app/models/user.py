from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict, field_validator


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def password_max_72_bytes(cls, v: str) -> str:
        if len(v.encode("utf-8")) > 72:
            raise ValueError("password must be at most 72 bytes (bcrypt limit)")
        return v


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    username: str
    created_at: datetime


class LoginIn(BaseModel):
    username: str
    password: str


class LoginOut(UserOut):
    access_token: str
    token_type: str = "bearer"