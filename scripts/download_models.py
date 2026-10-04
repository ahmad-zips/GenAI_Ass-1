"""Download the ONNX models from Google Drive into ./models  (pip install gdown).
Fill in the file IDs: Drive -> right-click the .onnx file -> Share -> 'Anyone with the link' -> copy the ID from the URL."""
import sys
from pathlib import Path

import gdown

FILE_IDS = {
    "task1_universal.onnx": "FILL_ME",
    "task2_classifier.onnx": "FILL_ME",
    "task2_specialist_salt_pepper.onnx": "FILL_ME",
    "task2_specialist_gaussian_blur.onnx": "FILL_ME",
    "task2_specialist_occlusion.onnx": "FILL_ME",
    "task3_soft_moe.onnx": "FILL_ME",
    "task4_generator.onnx": "FILL_ME",
}
dest = Path(__file__).resolve().parents[1] / "models"
dest.mkdir(exist_ok=True)
for name, fid in FILE_IDS.items():
    if fid == "FILL_ME":
        print(f"skip {name}: no file id set"); continue
    if (dest / name).exists():
        print(f"have {name}"); continue
    gdown.download(id=fid, output=str(dest / name), quiet=False)
print("done. Files in models/:", sorted(p.name for p in dest.glob("*.onnx")))
