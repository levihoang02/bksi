from datetime import datetime
import random
from typing import Dict, Any
from dataclasses import dataclass, field
from enum import Enum

class EventType(Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    NER = "NER"
    SUMMARIZE = "SUM"
    TAG = "TAG"

def generate_event_id() -> int:
    timestamp = int(datetime.utcnow().timestamp())
    random_part = random.randint(1000, 9999)
    return int(f"{timestamp}{random_part}")

@dataclass
class Event:
    source: str
    op: EventType
    payload: Dict[str, Any]
    id: int = field(default_factory=generate_event_id)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    version: str = field(default="1.0")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source": self.source,
            "op": self.op.value,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "version": self.version
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        return cls(
            id=data.get('id', generate_event_id()),
            source=data['source'],
            op=EventType(data['op']),
            payload=data['payload'],
            timestamp=data.get('timestamp', datetime.utcnow().isoformat()),
            version=data.get('version', "1.0")
        )

    def validate(self) -> bool:
        try:
            assert self.source, "Source is required"
            assert isinstance(self.payload, dict), "Payload must be a dictionary"
            assert self.op in EventType, f"Invalid operation type: {self.op}"
            return True
        except AssertionError as e:
            raise ValueError(f"Event validation failed: {str(e)}")
        
def debezium_to_event(debezium_msg: Dict[str, Any]) -> Event:
    try:
        op_type = debezium_msg.get('op')
        source = "debezium"

        # Choose payload based on the operation type
        if op_type == "c":
            payload = debezium_msg.get('after', {})
            op = EventType.CREATE
        # elif op_type == "u":
        #     payload = debezium_msg.get('after', {})
        #     op = EventType.UPDATE
        elif op_type == "d":
            payload = debezium_msg.get('before', {})  # <- use before for deletes
            op = EventType.DELETE
        else:
            raise ValueError(f"Skipping unsupported Debezium operation type: {op_type}")
        return Event(
            source=source,
            op=op,
            payload=payload,
            timestamp=datetime.utcnow().isoformat(),
            version="1.0"
        )
    except Exception as e:
        raise ValueError(f"Failed to convert Debezium message to event: {e}")