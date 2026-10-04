"""Image I/O helpers: validation, preprocessing, encoding, error maps."""
import base64
import io

import numpy as np
from fastapi import HTTPException, UploadFile
from PIL import Image, ImageOps, UnidentifiedImageError

SIZE = 128                       # all models were trained on 128x128 RGB
MAX_BYTES = 10 * 1024 * 1024     # 10 MB upload limit
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}


def read_image(file: UploadFile, resample=Image.BILINEAR) -> np.ndarray:
    """Validate an upload and return a float32 HxWx3 array in [0, 1] at 128x128."""
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, f"Unsupported file type '{file.content_type}'. Use JPEG, PNG or WebP.")
    data = file.file.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise HTTPException(413, "File too large (limit 10 MB).")
    if not data:
        raise HTTPException(400, "Empty file.")
    try:
        Image.open(io.BytesIO(data)).verify()                 # integrity check
        img = Image.open(io.BytesIO(data))
        img = ImageOps.exif_transpose(img).convert("RGB")     # phone photos carry EXIF rotation
    except (UnidentifiedImageError, OSError, ValueError):
        raise HTTPException(400, "The file is not a valid image.")
    img = img.resize((SIZE, SIZE), resample)
    return np.asarray(img, dtype=np.float32) / 255.0


def to_nchw(img01: np.ndarray) -> np.ndarray:
    return np.ascontiguousarray(img01.transpose(2, 0, 1)[None], dtype=np.float32)


def from_nchw(t: np.ndarray) -> np.ndarray:
    return t[0].transpose(1, 2, 0)


def to_data_uri(img01: np.ndarray) -> str:
    arr = (np.clip(img01, 0, 1) * 255.0 + 0.5).astype(np.uint8)
    buf = io.BytesIO()
    Image.fromarray(arr).save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def error_map(a: np.ndarray, b: np.ndarray, vmax: float = 0.5) -> np.ndarray:
    """Absolute error averaged over channels, drawn with a 'hot' colormap (black->red->yellow->white)."""
    v = np.clip(np.abs(a - b).mean(axis=2) / vmax, 0, 1)
    r = np.clip(3 * v, 0, 1)
    g = np.clip(3 * v - 1, 0, 1)
    bl = np.clip(3 * v - 2, 0, 1)
    return np.stack([r, g, bl], axis=2).astype(np.float32)


def psnr(a: np.ndarray, b: np.ndarray) -> float:
    mse = float(np.mean((a.astype(np.float64) - b.astype(np.float64)) ** 2))
    return 99.0 if mse < 1e-10 else float(10 * np.log10(1.0 / mse))


def mae(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.mean(np.abs(a - b)))
