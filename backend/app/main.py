"""FastAPI backend for the four generative-AI workspaces."""
import time
from contextlib import asynccontextmanager
from typing import Optional

import numpy as np
import onnxruntime as ort
from PIL import Image
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from . import corruptions, imaging
from .registry import Registry

CLASSES = ["clean", "salt_pepper", "blur", "occlusion"]       # order used by the Task 2 / Task 3 gate
EXPERT_KEY = {1: "salt_pepper", 2: "blur", 3: "occlusion"}
registry = Registry()
START = time.time()


@asynccontextmanager
async def lifespan(app):
    registry.warmup()          # first request should not pay the session-creation cost
    yield


app = FastAPI(title="GenAI Restoration & Sketch API", version="1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000", "http://localhost:5173"],
                   allow_methods=["*"], allow_headers=["*"])


# ------------------------------------------------------------------ helpers
def softmax(z):
    z = z - z.max()
    e = np.exp(z)
    return e / e.sum()


def prepare(file, corruption, severity, seed, sp_prob, blur_kernel, blur_sigma, occ_n, occ_area, sp_per_pixel=False):
    """Read the upload and (optionally) corrupt it at runtime.
    Returns (clean_reference_or_None, model_input, settings)."""
    img = imaging.read_image(file)
    if corruption in ("none", "already_corrupted"):
        ref = img if corruption == "none" else None            # no ground truth for user-supplied corrupted images
        return ref, img, {"corruption": corruption}
    params = dict(sp_prob=sp_prob, blur_kernel=blur_kernel, blur_sigma=blur_sigma, occ_n=occ_n, occ_area=occ_area)
    x, settings = corruptions.apply(img, corruption, severity, seed, params, sp_per_pixel)
    return img, x, settings


def package(ref, x, restored):
    """Common image + metric payload."""
    target = ref if ref is not None else x
    images = {"input": imaging.to_data_uri(x), "restored": imaging.to_data_uri(restored),
              "error_map": imaging.to_data_uri(imaging.error_map(restored, target))}
    if ref is not None:
        images["original"] = imaging.to_data_uri(ref)
    metrics = {"error_map_reference": "clean original" if ref is not None else "input image (no ground truth)"}
    if ref is not None:
        metrics.update(psnr_input=round(imaging.psnr(ref, x), 2), psnr_restored=round(imaging.psnr(ref, restored), 2),
                       mae_input=round(imaging.mae(ref, x), 4), mae_restored=round(imaging.mae(ref, restored), 4))
    return images, metrics


def restore_with(key, x):
    out, ms = registry.run(key, imaging.to_nchw(x))
    return np.clip(imaging.from_nchw(out[0]), 0, 1), ms


# ------------------------------------------------------------------ routes
@app.get("/api/health")
def health():
    st = registry.status()
    return {"status": "ok", "uptime_s": round(time.time() - START, 1), "onnxruntime": ort.__version__,
            "providers": ["CPUExecutionProvider"], "models_ready": sum(m["available"] for m in st.values()),
            "models_total": len(st), "models": st}


RESTORE_FORM = dict(corruption=Form("none"), severity=Form("medium"), seed=Form(None), sp_prob=Form(None),
                    blur_kernel=Form(None), blur_sigma=Form(None), occ_n=Form(None), occ_area=Form(None))


@app.post("/api/restore/universal")
def restore_universal(file: UploadFile = File(...), corruption: str = RESTORE_FORM["corruption"],
                      severity: str = RESTORE_FORM["severity"], seed: Optional[int] = RESTORE_FORM["seed"],
                      sp_prob: Optional[float] = RESTORE_FORM["sp_prob"], blur_kernel: Optional[int] = RESTORE_FORM["blur_kernel"],
                      blur_sigma: Optional[float] = RESTORE_FORM["blur_sigma"], occ_n: Optional[int] = RESTORE_FORM["occ_n"],
                      occ_area: Optional[float] = RESTORE_FORM["occ_area"]):
    ref, x, settings = prepare(file, corruption, severity, seed, sp_prob, blur_kernel, blur_sigma, occ_n, occ_area)
    restored, ms = restore_with("universal", x)
    images, metrics = package(ref, x, restored)
    return {"workspace": "universal", "images": images, "settings": settings, "metrics": metrics,
            "timing": {"inference_ms": round(ms, 2)}}


@app.post("/api/restore/hard")
def restore_hard(file: UploadFile = File(...), corruption: str = RESTORE_FORM["corruption"],
                 severity: str = RESTORE_FORM["severity"], seed: Optional[int] = RESTORE_FORM["seed"],
                 sp_prob: Optional[float] = RESTORE_FORM["sp_prob"], blur_kernel: Optional[int] = RESTORE_FORM["blur_kernel"],
                 blur_sigma: Optional[float] = RESTORE_FORM["blur_sigma"], occ_n: Optional[int] = RESTORE_FORM["occ_n"],
                 occ_area: Optional[float] = RESTORE_FORM["occ_area"], routing: str = Form("predicted")):
    if routing not in ("predicted", "oracle"):
        raise HTTPException(400, "routing must be 'predicted' or 'oracle'.")
    # the classifier and specialists were trained on whole-pixel salt-and-pepper noise
    ref, x, settings = prepare(file, corruption, severity, seed, sp_prob, blur_kernel, blur_sigma, occ_n, occ_area, True)

    out, clf_ms = registry.run("classifier", imaging.to_nchw(x))
    probs = softmax(out[0][0].astype(np.float64))                  # the exported classifier returns logits
    predicted = int(np.argmax(probs))

    oracle = None
    if corruption != "already_corrupted":
        oracle = 0 if corruption == "none" else CLASSES.index(corruption)
    if routing == "oracle":
        if oracle is None:
            raise HTTPException(400, "Oracle routing needs a known corruption label; choose a corruption or use predicted routing.")
        route = oracle
    else:
        route = predicted

    if route == 0:
        restored, expert_ms, expert = x.copy(), 0.0, "identity bypass"     # clean inputs are not processed
    else:
        restored, expert_ms = restore_with(EXPERT_KEY[route], x)
        expert = EXPERT_KEY[route]

    images, metrics = package(ref, x, restored)
    return {"workspace": "hard", "images": images, "settings": settings, "metrics": metrics,
            "routing": {"mode": routing, "probabilities": {c: round(float(p), 5) for c, p in zip(CLASSES, probs)},
                        "predicted": CLASSES[predicted], "oracle_label": None if oracle is None else CLASSES[oracle],
                        "routed_to": expert,
                        "classifier_correct": None if oracle is None else bool(predicted == oracle)},
            "timing": {"classifier_ms": round(clf_ms, 2), "expert_ms": round(expert_ms, 2),
                       "inference_ms": round(clf_ms + expert_ms, 2)}}


@app.post("/api/restore/soft")
def restore_soft(file: UploadFile = File(...), corruption: str = RESTORE_FORM["corruption"],
                 severity: str = RESTORE_FORM["severity"], seed: Optional[int] = RESTORE_FORM["seed"],
                 sp_prob: Optional[float] = RESTORE_FORM["sp_prob"], blur_kernel: Optional[int] = RESTORE_FORM["blur_kernel"],
                 blur_sigma: Optional[float] = RESTORE_FORM["blur_sigma"], occ_n: Optional[int] = RESTORE_FORM["occ_n"],
                 occ_area: Optional[float] = RESTORE_FORM["occ_area"]):
    ref, x, settings = prepare(file, corruption, severity, seed, sp_prob, blur_kernel, blur_sigma, occ_n, occ_area, True)
    out, ms = registry.run("soft_moe", imaging.to_nchw(x))
    restored = np.clip(imaging.from_nchw(out[0]), 0, 1)
    w = out[1][0].astype(np.float64)
    w = w / w.sum()
    ent = float(-(w * np.log(w + 1e-12)).sum() / np.log(len(w)))        # 0 = one expert, 1 = uniform
    images, metrics = package(ref, x, restored)
    names = ["clean (identity)", "salt_pepper", "blur", "occlusion"]
    return {"workspace": "soft", "images": images, "settings": settings, "metrics": metrics,
            "routing": {"weights": {n: round(float(v), 5) for n, v in zip(names, w)},
                        "dominant": names[int(np.argmax(w))], "normalized_entropy": round(ent, 4)},
            "timing": {"inference_ms": round(ms, 2)}}


@app.post("/api/sketch")
def sketch(file: UploadFile = File(...), style: int = Form(1)):
    if style not in (1, 2, 3):
        raise HTTPException(400, "style must be 1, 2 or 3.")
    photo = imaging.read_image(file, Image.BICUBIC)                    # same resampling as the FS2K training pipeline
    x = imaging.to_nchw(photo * 2.0 - 1.0)                             # the generator was trained on [-1, 1]
    out, ms = registry.run("sketch", x, np.array([style - 1], dtype=np.int64))
    sk = np.clip((imaging.from_nchw(out[0]) + 1.0) / 2.0, 0, 1)
    return {"workspace": "sketch", "style": style,
            "images": {"original": imaging.to_data_uri(photo), "sketch": imaging.to_data_uri(sk)},
            "timing": {"inference_ms": round(ms, 2)}}
