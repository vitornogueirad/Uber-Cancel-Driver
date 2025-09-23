from fastapi import APIRouter
import numpy as np
from ..model.loader import load_artifacts
from ..features.build_frame import build_frame, USE_COLS_CACHE
from .schemas import Ride, PredResponse

router = APIRouter()

CAL, SCHEMA, THR = load_artifacts()
# injeta ordem de colunas no builder
from ..features import build_frame as bf
bf.USE_COLS_CACHE = SCHEMA["feature_order"]

@router.get("/health")
def health():
    return {"status": "ok"}

@router.post("/predict", response_model=PredResponse)
def predict(x: Ride):
    df = build_frame(x.model_dump())
    p_cal = float(CAL.predict_proba(df)[:, 1])


    return {
        "prob_cancel_cal": round(p_cal, 6),
        "threshold": THR,
        "will_cancel": bool(p_cal >= THR)
    }
