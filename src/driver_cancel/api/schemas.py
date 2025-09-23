from pydantic import BaseModel, Field, constr
from typing import Optional

TimeStr = constr(pattern=r"^\d{2}:\d{2}(:\d{2})?$")
DateStr = constr(pattern=r"^\d{4}-\d{2}-\d{2}$")

class Ride(BaseModel):
    pickup_location: str
    drop_location: str
    vehicle_type: str
    payment_method: Optional[str] = None
    avg_vtat: Optional[float] = None
    date: DateStr # type: ignore
    time: TimeStr # type: ignore

class PredResponse(BaseModel):
    prob_cancel_cal: float
    threshold: float
    will_cancel: bool
