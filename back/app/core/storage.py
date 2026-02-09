from __future__ import annotations

import os
import re
from datetime import datetime, timezone
from pathlib import Path

from fastapi import UploadFile

from app.core.config import settings


_slug_re = re.compile(r"[^a-zA-Z0-9._-]+")


def _utcstamp() -> str:
    # 20260207T153012Z
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _safe_filename(name: str) -> str:
    name = name.strip().replace(" ", "_")
    name = _slug_re.sub("_", name)
    return name[:200] if len(name) > 200 else name


async def save_upload_to_media(file: UploadFile) -> dict:
    """
    Guarda el UploadFile en disco dentro de MEDIA_DIR.
    Retorna:
      {
        "abs_path": "...",
        "rel_path": "/media/...",
        "filename": "..."
      }
    """
    media_dir = Path(settings.media_dir)
    media_dir.mkdir(parents=True, exist_ok=True)

    orig = file.filename or "upload"
    safe = _safe_filename(orig)
    stamp = _utcstamp()

    # Subcarpeta por fecha para evitar miles de archivos en un solo dir
    day_dir = media_dir / stamp[:8]
    day_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{stamp}_{safe}"
    abs_path = day_dir / filename

    content = await file.read()
    abs_path.write_bytes(content)

    # Construye ruta relativa servida por StaticFiles
    # e.g. /media/20260207/20260207T..._x.jpg
    rel_fs = abs_path.relative_to(media_dir).as_posix()
    rel_url_path = f"{settings.media_url_prefix.rstrip('/')}/{rel_fs}"

    return {
        "abs_path": str(abs_path),
        "rel_path": rel_url_path,
        "filename": filename,
    }


def delete_media_by_rel_path(rel_path: str) -> None:
    """
    rel_path: /media/20260207/xxxx.jpg
    """
    prefix = settings.media_url_prefix.rstrip("/")
    if not rel_path.startswith(prefix + "/"):
        return

    rel_fs = rel_path[len(prefix) + 1 :]
    abs_path = Path(settings.media_dir) / rel_fs
    try:
        abs_path.unlink(missing_ok=True)
    except Exception:
        pass
