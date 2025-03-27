from pydantic import BaseModel, Json, field_validator
from datetime import datetime

class Event(BaseModel):
    id: int
    source: str
    type: str
    payload: Json