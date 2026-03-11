from __future__ import annotations

import random
from datetime import datetime, timezone

from bson import ObjectId
from fastapi import HTTPException

from app.db.mongo import get_db

#COLLECTION = "images"
COLLECTION = "images_clases"
GAME_ANSWERS_COLLECTION = "game_answers"

TAU_LOW = 0.33
TAU_HIGH = 0.66

NINE_CLASSES = [
    "High Prime",
    "Average Prime",
    "Low Prime",
    "High Choice",
    "Average Choice",
    "Low Choice",
    "High Select",
    "Low Select",
    "High Standard",
]

DISTANCE_MAP: dict[str, dict[str, list[str]]] = {
    "High Prime": {
        "close": ["Average Prime", "Low Prime"],
        "far": ["Low Select", "High Standard"],
    },
    "Average Prime": {
        "close": ["High Prime", "Low Prime"],
        "far": ["Low Select", "High Standard"],
    },
    "Low Prime": {
        "close": ["Average Prime", "High Choice"],
        "far": ["Low Select", "High Standard"],
    },
    "High Choice": {
        "close": ["Average Choice", "Low Prime"],
        "far": ["Low Select", "High Standard"],
    },
    "Average Choice": {
        "close": ["High Choice", "Low Choice"],
        "far": ["Low Select", "High Standard"],
    },
    "Low Choice": {
        "close": ["Average Choice", "High Select"],
        "far": ["High Prime", "High Standard"],
    },
    "High Select": {
        "close": ["Low Choice", "Low Select"],
        "far": ["High Prime", "Average Prime"],
    },
    "Low Select": {
        "close": ["High Select", "High Standard"],
        "far": ["High Prime", "Average Prime"],
    },
    "High Standard": {
        "close": ["Low Select", "High Select"],
        "far": ["High Prime", "Average Prime"],
    },
}


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _to_out(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]),
        "image_url": doc.get("image_url", ""),
        "true_class": doc.get("true_class"),
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
    async def get_random_for_game1(session_id: str) -> dict | None:
        """
        Algoritmo adaptativo de Juego 1.
        Usa:
        - historial de errores/aciertos de la sesión actual
        - score residual m(c) = n_err(c) - n_corr(c)
        - evita repetir imágenes usadas en la sesión
        - si no alcanza, reinicia U completo
        """
        db = get_db()

        grouped_images = await _get_images_grouped_by_class(db)
        if not grouped_images:
            return None

        history = await _get_session_history(db, session_id)
        residual_scores = _compute_residual_scores(history, NINE_CLASSES)
        used_ids = await _get_used_image_ids(db, session_id)

        anchor_class = _choose_anchor_class_game1(
            residual_scores=residual_scores,
            history=history,
            classes=NINE_CLASSES,
        )

        selected_doc = _pick_image_from_class(
            grouped_images=grouped_images,
            class_name=anchor_class,
            used_ids=used_ids,
        )

        # Si no hay imágenes disponibles no usadas, reiniciar U completo
        if selected_doc is None:
            selected_doc = _pick_image_from_class(
                grouped_images=grouped_images,
                class_name=anchor_class,
                used_ids=set(),
            )

        if selected_doc is None:
            return None

        return _to_out(selected_doc)

    #@staticmethod
    #async def get_images_for_game3() -> dict | None:
    @staticmethod
    async def get_images_for_game3(session_id: str) -> dict | None:
        db = get_db()

        grouped_images = await _get_images_grouped_by_class(db)
        if not grouped_images:
            return None

        history = await _get_session_history(db, session_id)
        error_rates = _compute_error_rates(history, NINE_CLASSES)
        used_ids = await _get_used_image_ids(db, session_id)

        anchor_class = _choose_anchor_class(error_rates, history, NINE_CLASSES)
        difficulty = _choose_difficulty(anchor_class, error_rates, history)

        selection = _try_select_game3_images(
            grouped_images=grouped_images,
            anchor_class=anchor_class,
            difficulty=difficulty,
            used_ids=used_ids,
        )

        if selection is None:
            selection = _try_select_game3_images(
                grouped_images=grouped_images,
                anchor_class=anchor_class,
                difficulty=difficulty,
                used_ids=set(),
            )

        if selection is None:
            return None

        correct_doc, distractor_b, distractor_c = selection

        images = [
            {"id": str(correct_doc["_id"]), "image_url": correct_doc.get("image_url", "")},
            {"id": str(distractor_b["_id"]), "image_url": distractor_b.get("image_url", "")},
            {"id": str(distractor_c["_id"]), "image_url": distractor_c.get("image_url", "")},
        ]
        random.shuffle(images)

        return {
            "target_class": anchor_class,
            "difficulty": difficulty,
            "correct_image_id": str(correct_doc["_id"]),
            "images": images,
        }

async def _get_images_grouped_by_class(db) -> dict[str, list[dict]]:
    docs = (
        await db[COLLECTION]
        .find(
            {
                "image_url": {"$ne": None},
                "true_class": {"$ne": None},
                "is_active": True,
                "source_type": "seeded",
            }
        )
        .to_list(length=5000)
    )

    by_class: dict[str, list[dict]] = {}
    for doc in docs:
        cls = doc["true_class"]
        by_class.setdefault(cls, []).append(doc)

    return by_class


async def _get_session_history(db, session_id: str) -> list[dict]:
    history = (
        await db[GAME_ANSWERS_COLLECTION]
        .find(
            {
                "session_id": session_id,
                "correct_answer": {"$ne": None},
                "user_answer": {"$ne": None},
                "game_type": {"$in": [1, 3]},
            }
        )
        .to_list(length=500)
    )
    return history


def _compute_error_rates(history: list[dict], classes: list[str]) -> dict[str, float]:
    n_true = {c: 0 for c in classes}
    n_err = {c: 0 for c in classes}

    for row in history:
        correct = row.get("correct_answer")
        user = row.get("user_answer")

        if correct in n_true:
            n_true[correct] += 1
            if user != correct:
                n_err[correct] += 1

    rates: dict[str, float] = {}
    for c in classes:
        rates[c] = (n_err[c] / n_true[c]) if n_true[c] > 0 else 0.0

    return rates


def _choose_anchor_class(
    error_rates: dict[str, float],
    history: list[dict],
    classes: list[str],
) -> str:
    if not history:
        return random.choice(classes)

    max_rate = max(error_rates.values())
    tied = [c for c, rate in error_rates.items() if rate == max_rate]
    return random.choice(tied)


def _choose_difficulty(
    anchor_class: str,
    error_rates: dict[str, float],
    history: list[dict],
) -> str:
    if not history:
        return "medium"

    rate = error_rates.get(anchor_class, 0.0)

    if rate >= TAU_HIGH:
        return "low"
    if rate >= TAU_LOW:
        return "medium"
    return "hard"


async def _get_used_image_ids(db, session_id: str) -> set[str]:
    rows = (
        await db[GAME_ANSWERS_COLLECTION]
        .find({"session_id": session_id})
        .to_list(length=500)
    )

    used: set[str] = set()

    for row in rows:
        image_id = row.get("image_id")
        correct_image_id = row.get("correct_image_id")
        user_answer = row.get("user_answer")

        if image_id:
            used.add(str(image_id))

        if correct_image_id:
            used.add(str(correct_image_id))

        if row.get("game_type") == 3 and user_answer:
            used.add(str(user_answer))

    return used


def _try_select_game3_images(
    grouped_images: dict[str, list[dict]],
    anchor_class: str,
    difficulty: str,
    used_ids: set[str],
) -> tuple[dict, dict, dict] | None:
    correct_doc = _pick_image_from_class(
        grouped_images=grouped_images,
        class_name=anchor_class,
        used_ids=used_ids,
    )
    if correct_doc is None:
        return None

    used_now = set(used_ids)
    used_now.add(str(correct_doc["_id"]))

    distractor_classes = _choose_distractor_classes(anchor_class, difficulty)
    if distractor_classes is None:
        return None

    class_b, class_c = distractor_classes

    distractor_b = _pick_image_from_class(
        grouped_images=grouped_images,
        class_name=class_b,
        used_ids=used_now,
    )
    if distractor_b is None:
        return None

    used_now.add(str(distractor_b["_id"]))

    distractor_c = _pick_image_from_class(
        grouped_images=grouped_images,
        class_name=class_c,
        used_ids=used_now,
    )
    if distractor_c is None:
        return None

    return correct_doc, distractor_b, distractor_c


def _choose_distractor_classes(anchor_class: str, difficulty: str) -> tuple[str, str] | None:
    rule = DISTANCE_MAP.get(anchor_class)
    if not rule:
        return None

    close_classes = rule["close"]
    far_classes = rule["far"]

    if difficulty == "low":
        if len(far_classes) < 2:
            return None
        chosen = random.sample(far_classes, 2)
        return chosen[0], chosen[1]

    if difficulty == "medium":
        if len(close_classes) < 1 or len(far_classes) < 1:
            return None
        return random.choice(close_classes), random.choice(far_classes)

    if len(close_classes) < 2:
        return None
    chosen = random.sample(close_classes, 2)
    return chosen[0], chosen[1]


def _pick_image_from_class(
    grouped_images: dict[str, list[dict]],
    class_name: str,
    used_ids: set[str],
) -> dict | None:
    docs = grouped_images.get(class_name, [])
    if not docs:
        return None

    available = [d for d in docs if str(d["_id"]) not in used_ids]

    if available:
        return random.choice(available)

    return None

def _compute_residual_scores(history: list[dict], classes: list[str]) -> dict[str, int]:
    """
    m(c) = n_err(c) - n_corr(c)
    donde:
    - n_err(c): fallos cuando la clase correcta era c
    - n_corr(c): aciertos cuando la clase correcta era c
    """
    n_err = {c: 0 for c in classes}
    n_corr = {c: 0 for c in classes}

    for row in history:
        correct = row.get("correct_answer")
        user = row.get("user_answer")

        if correct not in n_err:
            continue

        if user == correct:
            n_corr[correct] += 1
        else:
            n_err[correct] += 1

    return {c: n_err[c] - n_corr[c] for c in classes}


def _choose_anchor_class_game1(
    residual_scores: dict[str, int],
    history: list[dict],
    classes: list[str],
) -> str:
    """
    Regla del algoritmo:
    - si T = 0 -> clase aleatoria
    - si max m(c) > 0 -> elegir clase con mayor m(c)
    - en otro caso -> clase aleatoria
    - si hay empate, desempate aleatorio
    """
    if not history:
        return random.choice(classes)

    max_score = max(residual_scores.values())
    if max_score > 0:
        tied = [c for c, score in residual_scores.items() if score == max_score]
        return random.choice(tied)

    return random.choice(classes)