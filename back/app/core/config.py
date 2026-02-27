from __future__ import annotations
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]  # ajusta si tu estructura cambia


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Backend API"
    env: str = "local"
    log_level: str = "INFO"

    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db: str = "prediction_db"

    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    media_dir: str = "./media"
    media_url_prefix: str = "/media"
    public_base_url: str = "http://localhost:8000"

    jwt_secret: str = "key2307?-07022025"
    jwt_alg: str = "HS256"
    access_token_expire_minutes: int = 120

    auth_cookie_name: str = "access_token"
    auth_cookie_samesite: str = "lax"  # "lax"|"strict"|"none"
    auth_cookie_secure: bool = False

    quiz_target_class: str = "High Choice"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    def build_public_url(self, path: str) -> str:
        base = self.public_base_url.rstrip("/")
        p = path if path.startswith("/") else f"/{path}"
        return f"{base}{p}"


settings = Settings()


