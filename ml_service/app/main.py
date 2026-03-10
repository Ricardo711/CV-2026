from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile, status

from app.model import load_model, predict_image

app = FastAPI(title="CV2026 ML Service", version="1.0.0")


@app.on_event("startup")
async def startup() -> None:
    load_model()


@app.get("/health", status_code=status.HTTP_200_OK)
async def health() -> dict:
    return {"status": "ok"}


@app.post("/predict", status_code=status.HTTP_200_OK)
async def predict(file: UploadFile = File(...)) -> dict:
    suffix = Path(file.filename or "image.jpg").suffix or ".jpg"
    temp_path: str | None = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            temp_path = tmp.name

        result = predict_image(temp_path)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if temp_path:
            Path(temp_path).unlink(missing_ok=True)