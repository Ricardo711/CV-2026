from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from app.core.auth_deps import get_current_user
from app.core.config import settings
from app.core.constants import NINE_CLASSES
from app.core.storage import save_upload_to_media
from app.models.game_image import GameImageOut
from app.services.game_images_service import GameImagesService

router = APIRouter(prefix="/images", tags=["images"])


@router.post("", response_model=GameImageOut, status_code=status.HTTP_201_CREATED)
async def upload_labeled_image(
    file: UploadFile = File(...),
    marbling_class: str = Form(...),
    current_user: dict = Depends(get_current_user),
) -> GameImageOut:
    """
    Admin: sube una imagen etiquetada con su marbling_class (9-class).
    Valores válidos: High Prime, Average Prime, Low Prime,
                     High Choice, Average Choice, Low Choice,
                     High Select, Low Select, High Standard.
    Estas imágenes se usan en los Juegos 1 y 3.
    """
    if marbling_class not in NINE_CLASSES:
        raise HTTPException(
            status_code=422,
            detail=f"marbling_class debe ser uno de: {', '.join(NINE_CLASSES)}",
        )

    saved = await save_upload_to_media(file)
    image_url = settings.build_public_url(saved["rel_path"])

    created = await GameImagesService.create(
        image_path=saved["rel_path"],
        image_url=image_url,
        marbling_class=marbling_class,
    )
    return created
