from abc import ABC, abstractmethod
import requests
from kafka_utils.event import Event, EventType
from kafka_utils.producer import producer
from utils.config import Config

config = Config()


class AbstractModelRouter(ABC):
    def __init__(self, task_name: str):
        self.gateway_base = f"http://{config.GATE_WAY}/route"
        self.task = task_name  # "ner", "tag", "summarize"

    def build_payload(self, ticket_id, content) -> dict:
        new_payload = {
            "ticket_id": ticket_id,
            "content":  content
        }
        return new_payload
    
    def build_event(self, source, op):
        event = {
            "source": source, 
            "op": op,
            "payload": self.build_payload()
        }
        return event

    def route(self, mode, op, ticket_id, content) -> dict:
        payload = self.build_payload(ticket_id, content)
        if mode == "sync":
            route_url = f"{self.gateway_base}/{self.task}"
            try:
                route_response = requests.post(route_url, timeout=5)
                route_response.raise_for_status()
                route_data = route_response.json()
                instance_url = route_data.get("url")
                if not instance_url:
                    raise ValueError("No instance URL returned from routing service.")
            except Exception as e:
                raise RuntimeError(f"Failed to route through gateway: {str(e)}")

            try:
                headers = {
                    "Content-Type": "application/json",
                }
                response = requests.post(instance_url, json=payload, headers=headers)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                raise RuntimeError(f"Error calling model instance at {instance_url}: {str(e)}")

        elif mode == "async":
            route_url = f"{self.gateway_base}/{self.task}"
            try:
                route_response = requests.post(route_url, timeout=5)
                route_response.raise_for_status()
                route_data = route_response.json()
                topic = route_data.get("topic") or f"{route_data.get('service_name')}-{route_data.get('id')}"
            except Exception as e:
                raise RuntimeError(f"Failed to route for async mode: {str(e)}")

            try:
                event = Event(
                    source="ticket",
                    op=op,
                    payload=payload
                )
                producer.send_event(topic=topic, event=event)
                return {"status": "queued", "routed_topic": topic}
            except Exception as e:
                raise RuntimeError(f"Failed to produce Kafka event: {str(e)}")

        else:
            raise ValueError(f"Unsupported mode '{mode}'")

class NerModelRouter(AbstractModelRouter):
    def __init__(self):
        super().__init__(task_name="ner")
        
class TagModelRouter(AbstractModelRouter):
    def __init__(self):
        super().__init__(task_name="tag")


class SummaryModelRouter(AbstractModelRouter):
    def __init__(self):
        super().__init__(task_name="summarize")
        
class AISampleRouter(AbstractModelRouter):
    def __init__(self):
        super().__init__(task_name="ai-sample")