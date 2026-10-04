import os, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
os.environ["MODELS_DIR"] = str(ROOT / "models_dummy")
sys.path.insert(0, str(ROOT / "backend"))
