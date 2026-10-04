"""Runtime corruptions that mirror the assignment definitions (and the Task 1 notebook)."""
from typing import Optional

import numpy as np
from fastapi import HTTPException

KINDS = ("salt_pepper", "blur", "occlusion")
SEVERITY_PRESETS = {                       # fixed test-time levels from the assignment
    "salt_pepper": {"low": 0.03, "medium": 0.08, "high": 0.15},
    "blur": {"low": (3, 0.7), "medium": (5, 1.5), "high": (7, 2.5)},
    "occlusion": {"low": (1, 0.10), "medium": (2, 0.20), "high": (3, 0.35)},
}


def salt_pepper(img, p, rng, per_pixel=False):
    """per_pixel=False: every colour value is corrupted independently (Task 1 training noise).
    per_pixel=True : a corrupted pixel turns fully black/white in all 3 channels (Task 2/3 training noise)."""
    out = img.copy()
    if per_pixel:
        rv = rng.random(img.shape[:2])[:, :, None]      # one random value per pixel, shared by R, G, B
        out = np.where(rv < p / 2, 1.0, np.where(rv < p, 0.0, out)).astype(np.float32)
        return out
    rv = rng.random(img.shape)
    out[rv < p / 2] = 1.0
    out[(rv >= p / 2) & (rv < p)] = 0.0
    return out


def _gauss_kernel(k, sigma):
    x = np.linspace(-(k - 1) * 0.5, (k - 1) * 0.5, k)
    ker = np.exp(-0.5 * (x / sigma) ** 2)
    return (ker / ker.sum()).astype(np.float32)


def gaussian_blur(img, k, sigma):
    """Separable Gaussian blur with reflect padding (same semantics as torchvision's gaussian_blur)."""
    h, w, _ = img.shape
    ker, r = _gauss_kernel(k, sigma), k // 2
    p = np.pad(img, ((r, r), (r, r), (0, 0)), mode="reflect")
    tmp = sum(ker[i] * p[:, i:i + w, :] for i in range(k))
    return sum(ker[i] * tmp[i:i + h] for i in range(k)).astype(np.float32)


def occlusion(img, n, area, rng):
    """n black rectangles whose total area is ~`area` of the image. Returns (image, boxes, coverage)."""
    h, w, _ = img.shape
    mask = np.zeros((h, w), bool)
    boxes = []
    per_rect = area * h * w / n
    for _ in range(n):
        ratio = rng.uniform(0.6, 1.6)
        rh = int(np.clip(round(np.sqrt(per_rect * ratio)), 4, h))
        rw = int(np.clip(round(per_rect / rh), 4, w))
        top, left = int(rng.integers(0, h - rh + 1)), int(rng.integers(0, w - rw + 1))
        mask[top:top + rh, left:left + rw] = True
        boxes.append([top, left, rh, rw])
    out = img.copy()
    out[mask] = 0.0
    return out, boxes, float(mask.mean())


def apply(img, kind: str, severity: str, seed: Optional[int], params: dict, sp_per_pixel: bool = False):
    """Apply a corruption. Returns (corrupted image, settings dict that is echoed to the UI)."""
    if kind not in KINDS:
        raise HTTPException(400, f"Unknown corruption '{kind}'.")
    seed = int(seed) if seed is not None else int(np.random.SeedSequence().entropy % (2**31))
    rng = np.random.default_rng(seed)
    custom = severity == "custom"
    if not custom and severity not in ("low", "medium", "high"):
        raise HTTPException(400, "severity must be low, medium, high or custom.")
    settings = {"corruption": kind, "severity": severity, "seed": seed}

    if kind == "salt_pepper":
        p = params.get("sp_prob") if custom else SEVERITY_PRESETS[kind][severity]
        p = 0.08 if p is None else p
        if not 0.0 <= p <= 0.5:
            raise HTTPException(400, "sp_prob must be in [0, 0.5].")
        settings["probability"] = round(float(p), 4)
        settings["noise_model"] = "per-pixel (Task 2/3 training)" if sp_per_pixel else "per-channel (Task 1 training)"
        return salt_pepper(img, p, rng, sp_per_pixel), settings

    if kind == "blur":
        k, s = (params.get("blur_kernel"), params.get("blur_sigma")) if custom else SEVERITY_PRESETS[kind][severity]
        k, s = (5 if k is None else int(k)), (1.5 if s is None else float(s))
        if k % 2 == 0 or not 3 <= k <= 15 or not 0.1 <= s <= 5.0:
            raise HTTPException(400, "blur_kernel must be odd in [3, 15] and blur_sigma in [0.1, 5].")
        settings.update(kernel_size=k, sigma=round(s, 3))
        return gaussian_blur(img, k, s), settings

    n, a = (params.get("occ_n"), params.get("occ_area")) if custom else SEVERITY_PRESETS[kind][severity]
    n, a = (2 if n is None else int(n)), (0.2 if a is None else float(a))
    if not 1 <= n <= 3 or not 0.05 <= a <= 0.5:
        raise HTTPException(400, "occ_n must be 1-3 and occ_area in [0.05, 0.5].")
    out, boxes, cov = occlusion(img, n, a, rng)
    settings.update(rectangles=n, target_area=round(a, 3), actual_coverage=round(cov, 3), boxes=boxes)
    return out, settings
