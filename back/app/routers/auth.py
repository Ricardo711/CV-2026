from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status

from app.core.config import settings
from app.core.security import create_access_token
from app.core.auth_deps import get_current_user
from app.models.user import UserCreate, UserOut, LoginIn, LoginOut
from app.services.users_service import UsersService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate):
    return await UsersService.create_user(
        email=payload.email,
        password=payload.password,
        full_name=payload.full_name,
    )


@router.post("/login", response_model=LoginOut)
async def login(payload: LoginIn, response: Response):
    user = await UsersService.authenticate(payload.email, payload.password)

    token = create_access_token(subject=user["id"])

    response.set_cookie(
        key=settings.auth_cookie_name,
        value=token,
        httponly=True,
        secure=settings.auth_cookie_secure,
        samesite=settings.auth_cookie_samesite,
        path="/",
        max_age=settings.access_token_expire_minutes * 60,
    )

    return {
        **user,
        "access_token": token,
        "token_type": "bearer",
    }


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response):
    response.delete_cookie(
        key=settings.auth_cookie_name,
        path="/",
    )
    return None


@router.get("/me", response_model=UserOut)
async def me(current_user: dict = Depends(get_current_user)):
    return current_user
