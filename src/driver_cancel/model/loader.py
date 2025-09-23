import joblib
from pathlib import Path
from ..utils.io import load_json
from ..core.config import settings

def load_artifacts():
    art = Path(settings.artifact_dir)
    cal = joblib.load(art / "uber_cancel_driver_clf.joblib")
    schema = load_json(art / "model_schema.json")
    thr = load_json(art / "threshold.json")["threshold"]
    return cal, schema, thr
