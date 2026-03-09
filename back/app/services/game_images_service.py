from __future__ import annotations

import random
from datetime import datetime, timezone

from bson import ObjectId
from fastapi import HTTPException

from app.db.mongo import get_db

COLLECTION = "images"


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _to_out(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]),
        "image_url": doc.get("image_url", ""),
        "marbling_class": doc.get("marbling_class"),
        "created_at": doc.get("created_at"),
    }


class GameImagesService:
    @staticmethod
    async def create(
        image_path: str,
        image_url: str,
        marbling_class: str,
    ) -> dict:
        """
        Guarda una imagen etiquetada en la colección.
        marbling_class debe ser uno de los 9 valores (High Prime, Average Choice, etc.).
        """
        db = get_db()
        doc = {
            "image_path": image_path,
            "image_url": image_url,
            "marbling_class": marbling_class,
            "created_at": _utcnow(),
        }
        res = await db[COLLECTION].insert_one(doc)
        return {"id": str(res.inserted_id), **doc}

    @staticmethod
    async def get(image_id: str) -> dict:
        db = get_db()
        try:
            _id = ObjectId(image_id)
        except Exception:
            raise HTTPException(status_code=400, detail="image_id inválido")

        doc = await db[COLLECTION].find_one({"_id": _id})
        if not doc:
            raise HTTPException(status_code=404, detail="Imagen no encontrada")
        return _to_out(doc)

    @staticmethod
    async def get_random_for_game1() -> dict | None:
        """
        Retorna una imagen aleatoria con marbling_class definida.
        Retorna None si la colección está vacía.
        """
        db = get_db()
        docs = await db[COLLECTION].find(
            {"marbling_class": {"$ne": None}}
        ).to_list(length=200)

        if not docs:
            return None
        return _to_out(random.choice(docs))

    @staticmethod
    async def get_images_for_game3() -> dict | None:
        """
        Retorna {target_class, correct_image_id, images} con 3 imágenes mezcladas
        (1 de la clase objetivo + 2 de clases distintas), todas con marbling_class definida.
        Retorna None si no hay imágenes suficientes → el router usa placeholders.
        """
        db = get_db()
        labeled_docs = await db[COLLECTION].find(
            {"marbling_class": {"$ne": None}}
        ).to_list(length=200)

        if not labeled_docs:
            return None

        # Agrupar por marbling_class para elegir una clase con al menos 1 imagen
        by_class: dict[str, list[dict]] = {}
        for doc in labeled_docs:
            cls = doc["marbling_class"]
            by_class.setdefault(cls, []).append(doc)

        available_classes = list(by_class.keys())
        if not available_classes:
            return None

        target_class = random.choice(available_classes)
        correct_doc = random.choice(by_class[target_class])
        correct_image_id = str(correct_doc["_id"])

        # Imágenes incorrectas: cualquier otra clase disponible
        wrong_docs = [d for d in labeled_docs if d["marbling_class"] != target_class]

        images = [
            {"id": correct_image_id, "image_url": correct_doc.get("image_url", "")},
        ]

        if len(wrong_docs) >= 2:
            two_wrong = random.sample(wrong_docs, 2)
        elif len(wrong_docs) == 1:
            two_wrong = wrong_docs + [None]  # type: ignore[list-item]
        else:
            two_wrong = [None, None]  # type: ignore[list-item]

        for w in two_wrong:
            if w:
                images.append({"id": str(w["_id"]), "image_url": w.get("image_url", "")})
            else:
                images.append({"id": "placeholder-wrong", "image_url": ""})

        random.shuffle(images)

        return {
            "target_class": target_class,
            "correct_image_id": correct_image_id,
            "images": images,
        }
