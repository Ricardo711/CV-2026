import io
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image

import torch
from torchvision import models, transforms

app = FastAPI()

# Allow browser frontends (local testing). Tighten later.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DEVICE = "cpu"

# 1) Load MobileNetV3-Large (pretrained on ImageNet)
# Note: On first run it will download weights automatically.
model = models.mobilenet_v3_large(weights=models.MobileNet_V3_Large_Weights.IMAGENET1K_V1)
model.eval()
model.to(DEVICE)

# 2) Use the official preprocessing associated with the weights
weights = models.MobileNet_V3_Large_Weights.IMAGENET1K_V1
preprocess = weights.transforms()

# 3) Optional: human-readable ImageNet labels (included with torchvision weights metadata)
IMAGENET_LABELS = weights.meta["categories"]

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    # Read image bytes
    image_bytes = await file.read()

    # Decode into PIL image
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    # Preprocess -> tensor [1,3,H,W]
    x = preprocess(img).unsqueeze(0).to(DEVICE)

    # Inference
    with torch.no_grad():
        logits = model(x)                    # [1, 1000]
        probs = torch.softmax(logits, dim=1) # [1, 1000]

        conf, idx = torch.max(probs, dim=1)  # each is shape [1]
        conf = float(conf.item())
        idx = int(idx.item())

    return {
        "predicted_index": idx,
        "predicted_label": IMAGENET_LABELS[idx],
        "confidence": conf,
    }
