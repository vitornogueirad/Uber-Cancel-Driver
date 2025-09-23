from fastapi.testclient import TestClient
from src.driver_cancel.api.service import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200 and r.json()["status"] == "ok"

def test_predict_smoke():
    payload = {
        "pickup_location": "Khandsa",
        "drop_location": "Malviya Nagar",
        "vehicle_type": "Premier Sedan",
        "payment_method": "UPI",
        "avg_vtat": 9.5,
        "date": "2025-06-15",
        "time": "08:50:00"
    }
    r = client.post("/predict", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "prob_cancel_cal" in data and "will_cancel" in data
