from __future__ import annotations

from pathlib import Path

import torch
import torch.nn as nn
from PIL import Image
from torchvision import models, transforms

BASE_DIR = Path(__file__).resolve().parents[2]
MODEL_PATH = BASE_DIR / "models" / "best.pt"
DEVICE = torch.device("cpu")

model = None
class_names: list[str] = []
image_size: int = 224
transform = None


def load_model() -> None:
    global model, class_names, image_size, transform

    # checkpoint = torch.load(MODEL_PATH, map_location=DEVICE)
    checkpoint = torch.load(MODEL_PATH, map_location=DEVICE, weights_only=False)

    config = checkpoint["config"]
    class_names = checkpoint["class_names"]
    image_size = int(config.get("image_size", 224))
    num_classes = len(class_names)
    dropout = float(config.get("head_dropout", 0.2))

    model_instance = models.densenet169(weights=None)

    in_features = model_instance.classifier.in_features
    model_instance.classifier = nn.Sequential(
        nn.Dropout(dropout),
        nn.Linear(in_features, num_classes),
    )

    model_instance.load_state_dict(checkpoint["model_state"])
    model_instance.to(DEVICE)
    model_instance.eval()

    model = model_instance

    transform = transforms.Compose(
        [
            transforms.Resize((image_size, image_size)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225],
            ),
        ]
    )


def predict_image(image_path: str) -> dict:
    if model is None or transform is None:
        raise RuntimeError("Model is not loaded")

    image = Image.open(image_path).convert("RGB")
    x = transform(image).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        logits = model(x)
        probs = torch.softmax(logits, dim=1)
        confidence, predicted_idx = torch.max(probs, dim=1)

    idx = int(predicted_idx.item())

    return {
        "predicted_index": idx,
        "predicted_label": class_names[idx],
        "confidence": float(confidence.item()),
        "class_names": class_names,
    }
