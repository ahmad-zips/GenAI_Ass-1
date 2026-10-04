import io
import numpy as np
import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.main import app

client = TestClient(app)


def img_bytes(fmt="PNG", size=(200, 150)):
    rng = np.random.default_rng(1)
    buf = io.BytesIO(); Image.fromarray(rng.integers(0, 255, (*size[::-1], 3), dtype=np.uint8)).save(buf, fmt)
    return buf.getvalue()


def post(path, data=None, content=None, ctype="image/png"):
    return client.post(path, files={"file": ("t.png", content or img_bytes(), ctype)}, data=data or {})


def test_health():
    j = client.get("/api/health").json()
    assert j["status"] == "ok" and j["models_ready"] == 7


@pytest.mark.parametrize("kind", ["none", "salt_pepper", "blur", "occlusion", "already_corrupted"])
def test_universal(kind):
    r = post("/api/restore/universal", {"corruption": kind, "severity": "high", "seed": 1})
    assert r.status_code == 200, r.text
    j = r.json()
    assert j["images"]["restored"].startswith("data:image/png;base64,") and j["timing"]["inference_ms"] >= 0
    assert ("original" in j["images"]) == (kind != "already_corrupted")


def test_corruption_reproducible_and_levels():
    a = post("/api/restore/universal", {"corruption": "occlusion", "severity": "high", "seed": 7}).json()
    b = post("/api/restore/universal", {"corruption": "occlusion", "severity": "high", "seed": 7}).json()
    assert a["images"]["input"] == b["images"]["input"]
    assert 0.25 < a["settings"]["actual_coverage"] <= 0.40
    s = post("/api/restore/universal", {"corruption": "blur", "severity": "medium"}).json()["settings"]
    assert (s["kernel_size"], s["sigma"]) == (5, 1.5)
    c = post("/api/restore/universal", {"corruption": "salt_pepper", "severity": "custom", "sp_prob": 0.1}).json()["settings"]
    assert c["probability"] == 0.1


def test_hard_predicted_and_oracle():
    j = post("/api/restore/hard", {"corruption": "blur", "severity": "low", "seed": 3}).json()
    p = j["routing"]["probabilities"]
    assert abs(sum(p.values()) - 1) < 1e-3 and j["routing"]["routed_to"] in ("identity bypass", "salt_pepper", "blur", "occlusion")
    o = post("/api/restore/hard", {"corruption": "blur", "routing": "oracle"}).json()
    assert o["routing"]["routed_to"] == "blur"
    c = post("/api/restore/hard", {"corruption": "none", "routing": "oracle"}).json()
    assert c["routing"]["routed_to"] == "identity bypass" and c["timing"]["expert_ms"] == 0
    assert post("/api/restore/hard", {"corruption": "already_corrupted", "routing": "oracle"}).status_code == 400


def test_soft():
    j = post("/api/restore/soft", {"corruption": "salt_pepper"}).json()
    assert abs(sum(j["routing"]["weights"].values()) - 1) < 1e-3 and len(j["routing"]["weights"]) == 4


def test_sketch():
    for s in (1, 2, 3):
        j = post("/api/sketch", {"style": s}).json()
        assert j["style"] == s and "sketch" in j["images"]
    assert post("/api/sketch", {"style": 4}).status_code == 400


def test_validation():
    assert post("/api/restore/universal", content=b"hello", ctype="text/plain").status_code == 400
    assert post("/api/restore/universal", content=b"not an image", ctype="image/png").status_code == 400
    assert post("/api/restore/universal", {"corruption": "fog"}).status_code == 400
    assert post("/api/restore/universal", {"corruption": "blur", "severity": "custom", "blur_kernel": 4}).status_code == 400
    assert post("/api/restore/universal", content=b"0" * (10 * 1024 * 1024 + 5)).status_code == 413
    assert post("/api/restore/universal", content=img_bytes("JPEG"), ctype="image/jpeg").status_code == 200


def test_salt_pepper_noise_models():
    import numpy as np
    from app import corruptions
    img = np.full((128, 128, 3), 0.5, np.float32)
    pix = corruptions.salt_pepper(img, 0.1, np.random.default_rng(0), per_pixel=True)
    assert np.all(pix[..., 0] == pix[..., 1]) and np.all(pix[..., 1] == pix[..., 2])   # whole pixel flips together
    chn = corruptions.salt_pepper(img, 0.1, np.random.default_rng(0), per_pixel=False)
    assert not np.all(chn[..., 0] == chn[..., 1])                                       # channels independent
    assert abs((pix != 0.5).any(axis=2).mean() - 0.1) < 0.02
    h = post("/api/restore/hard", {"corruption": "salt_pepper", "severity": "high", "seed": 1}).json()
    assert "per-pixel" in h["settings"]["noise_model"]
    u = post("/api/restore/universal", {"corruption": "salt_pepper", "severity": "high", "seed": 1}).json()
    assert "per-channel" in u["settings"]["noise_model"]
