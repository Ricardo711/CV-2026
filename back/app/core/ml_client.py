from __future__ import annotations

from pathlib import Path

import httpx

from app.core.config import settings


async def predict_with_ml_service(file_path: str) -> dict:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {file_path}")

    content_type = _guess_content_type(path.suffix.lower())

    async with httpx.AsyncClient(timeout=120.0) as client:
        with path.open("rb") as f:
            files = {
                "file": (path.name, f, content_type),
            }

            response = await client.post(
                f"{settings.ml_service_url.rstrip('/')}/predict",
                files=files,
            )

            response.raise_for_status()
            return response.json()


def _guess_content_type(ext: str) -> str:
    if ext in {".jpg", ".jpeg"}:
        return "image/jpeg"
    if ext == ".png":
        return "image/png"
    if ext == ".webp":
        return "image/webp"
    return "application/octet-stream"