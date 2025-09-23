from datetime import datetime
import pandas as pd
from ..core.config import settings

USE_COLS_CACHE = None  # preenchido pelo loader na inicialização da API

def build_frame(payload: dict) -> pd.DataFrame:
    # payload já validado pela camada Pydantic
    d = {
        "Pickup Location": payload.get("pickup_location"),
        "Drop Location":   payload.get("drop_location"),
        "Vehicle Type":    payload.get("vehicle_type"),
        "Payment Method":  payload.get("payment_method"),
        "Avg VTAT":        payload.get("avg_vtat"),
    }
    hhmmss = payload["time"] if len(payload["time"].split(":")) == 3 else payload["time"] + ":00"
    dt = datetime.fromisoformat(f"{payload['date']} {hhmmss}")

    d["hour"] = dt.hour
    d["day_of_week"] = dt.weekday()
    d["is_weekend"] = 1 if d["day_of_week"] in (5, 6) else 0

    # alinha com a ordem do treino
    assert USE_COLS_CACHE is not None, "USE_COLS_CACHE não carregado"
    return pd.DataFrame([d], columns=USE_COLS_CACHE).fillna({"Payment Method": "Unknown"})
