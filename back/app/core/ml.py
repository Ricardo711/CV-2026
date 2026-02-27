from __future__ import annotations

import torch
from torchvision import models

DEVICE = "cpu"

# Pesos y preprocess oficial
weights = models.MobileNet_V3_Large_Weights.IMAGENET1K_V1
preprocess = weights.transforms()
IMAGENET_LABELS = weights.meta["categories"]

model = models.mobilenet_v3_large(weights=weights)
model.eval()
model.to(DEVICE)


@torch.inference_mode()
def predict_pil_image(pil_img):
    x = preprocess(pil_img).unsqueeze(0).to(DEVICE)
    logits = model(x)
    probs = torch.softmax(logits, dim=1)

    conf, idx = torch.max(probs, dim=1)
    conf_f = float(conf.item())
    idx_i = int(idx.item())

    return {
        "predicted_index": idx_i,
        "predicted_label": IMAGENET_LABELS[idx_i],
        "confidence": conf_f,
    }
