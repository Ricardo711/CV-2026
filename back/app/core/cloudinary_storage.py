from __future__ import annotations

import cloudinary
import cloudinary.uploader

from app.core.config import settings


# Configuración al importar
if settings.cloudinary_url:
    cloudinary.config(cloudinary_url=settings.cloudinary_url, secure=True)
else:
    cloudinary.config(
        cloud_name=settings.cloudinary_cloud_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True,
    )


def upload_image(
    local_path: str,
    folder: str = "cv2026",
    filename: str | None = None,
) -> dict:
    """
    Sube una imagen local a Cloudinary y regresa metadatos útiles.
    """

    upload_options = {
        "folder": folder,
        "resource_type": "image",
    }

    if filename:
        upload_options["public_id"] = filename

    result = cloudinary.uploader.upload(
        local_path,
        **upload_options,
    )

    return {
        "public_id": result["public_id"],
        "secure_url": result["secure_url"],
        "version": result.get("version"),
        "format": result.get("format"),
        "bytes": result.get("bytes"),
        "width": result.get("width"),
        "height": result.get("height"),
    }