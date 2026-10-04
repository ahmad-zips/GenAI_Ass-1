"""Lazy ONNX model registry with timing."""
import os
import threading
import time
from pathlib import Path

import numpy as np
import onnxruntime as ort
from fastapi import HTTPException

MODEL_FILES = {
    "universal": "task1_universal.onnx",
    "classifier": "task2_classifier.onnx",
    "salt_pepper": "task2_specialist_salt_pepper.onnx",
    "blur": "task2_specialist_gaussian_blur.onnx",
    "occlusion": "task2_specialist_occlusion.onnx",
    "soft_moe": "task3_soft_moe.onnx",
    "sketch": "task4_generator.onnx",
}


class Registry:
    def __init__(self, models_dir=None):
        self.dir = Path(models_dir or os.environ.get("MODELS_DIR", "/models"))
        self._sessions, self._lock = {}, threading.Lock()

    def status(self):
        out = {}
        for key, fname in MODEL_FILES.items():
            p = self.dir / fname
            out[key] = {"file": fname, "available": p.exists(),
                        "size_mb": round(p.stat().st_size / 1e6, 2) if p.exists() else None,
                        "loaded": key in self._sessions}
        return out

    def get(self, key):
        if key in self._sessions:
            return self._sessions[key]
        with self._lock:
            if key in self._sessions:
                return self._sessions[key]
            path = self.dir / MODEL_FILES[key]
            if not path.exists():
                raise HTTPException(503, f"Model file '{path.name}' was not found in the models directory.")
            try:
                opts = ort.SessionOptions()
                opts.log_severity_level = 3
                sess = ort.InferenceSession(str(path), opts, providers=["CPUExecutionProvider"])
            except Exception as e:                                   # corrupt / incompatible file
                raise HTTPException(500, f"Could not load '{path.name}': {e}")
            self._sessions[key] = sess
            return sess

    def run(self, key, *arrays):
        """Run a model with positional inputs; returns (outputs, milliseconds)."""
        sess = self.get(key)
        feeds = {i.name: a for i, a in zip(sess.get_inputs(), arrays)}
        t0 = time.perf_counter()
        out = sess.run(None, feeds)
        return out, (time.perf_counter() - t0) * 1000.0

    def warmup(self):
        x = np.zeros((1, 3, 128, 128), np.float32)
        for key in MODEL_FILES:
            if (self.dir / MODEL_FILES[key]).exists():
                try:
                    args = (x, np.zeros((1,), np.int64)) if key == "sketch" else (x,)
                    self.run(key, *args)
                except Exception as e:
                    print(f"[warmup] {key} failed: {e}")
