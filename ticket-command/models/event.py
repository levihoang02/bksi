from pydantic import BaseModel, Field
from datetime import datetime
import random

def generate_event_id() -> int:
    timestamp = int(datetime.utcnow().timestamp())
    random_part = random.randint(1000, 9999)
    return int(f"{timestamp}{random_part}")

class Event(BaseModel):
    id: int = Field(default_factory=generate_event_id, description="ID")
    source: str
    op: str
    payload: dict
