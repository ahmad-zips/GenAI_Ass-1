# GenAI Studio — restoration autoencoders & face-to-sketch cGAN

One browser app with four workspaces: **Universal Restoration** (Task 1), **Hard-Routed Restoration** (Task 2),
**Soft Mixture-of-Experts** (Task 3) and **Face-to-Sketch Generator** (Task 4).
React + Tailwind frontend → nginx → FastAPI → ONNX Runtime. Everything runs in Docker.

## Run (one command)
1. Put the 7 `.onnx` files in `./models` (see `models/README.md`, or `python scripts/download_models.py`).
2. `docker compose up --build`
3. Open http://localhost:3000

The sidebar shows backend status and which model files were found. Missing models only disable the matching workspace (HTTP 503 with a clear message).

## Develop without Docker / without trained models
```bash
python tools/make_dummy_models.py models_dummy          # placeholder ONNX files with the real I/O contract
cd backend && pip install -r requirements.txt pytest httpx
MODELS_DIR=../models_dummy uvicorn app.main:app --port 8000 --reload
cd ../frontend && npm install && npm run dev            # http://localhost:5173 (proxies /api to :8000)
cd ../backend && python -m pytest tests -q              # API tests (use the dummy models)
```

## API
| Method | Path | Purpose |
|---|---|---|
| GET | `/api/health` | status, ORT version, which model files exist |
| POST | `/api/restore/universal` | Task 1 |
| POST | `/api/restore/hard` | Task 2 (`routing=predicted\|oracle`) |
| POST | `/api/restore/soft` | Task 3 |
| POST | `/api/sketch` | Task 4 (`style=1\|2\|3`) |

Restoration forms: `file`, `corruption` (`none|salt_pepper|blur|occlusion|already_corrupted`), `severity` (`low|medium|high|custom`), optional `seed`
and custom parameters. Fixed levels follow the assignment: salt-and-pepper 0.03/0.08/0.15, blur (3,0.7)/(5,1.5)/(7,2.5), occlusion 1/2/3 rectangles for ~10/20/35 %.
