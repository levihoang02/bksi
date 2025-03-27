from abc import ABC, abstractmethod
from models.event import Event
from kafka_utils.producer import KafkaProducerService
from utils.config import Config
from helpers.html import decode_html

config = Config()

producer_config = {
        "bootstrap.servers": config.KAFKA_BROKERS_INTERNAL,
        "client.id": "ticket-producer",
        "acks": "all"
}

producer = KafkaProducerService(producer_config)

class AbstractEventHandler(ABC):
    @abstractmethod
    def handle_event(self, event: dict):
        pass
    
class InsertEventHandler(AbstractEventHandler):
    def handle_event(self, event: dict):
        new_data = event["after"]
        if(new_data["created_by"] == "customer"):
            raw_content = decode_html(new_data["message"])
            payload = {
                "ticket_id": new_data["id"],
                "content":  raw_content
            }
            event = Event(
                source= 'ticket-command',
                op= 'c',
                payload= payload
            )
            return producer.send_message('tickets', event)

class UpdateEventHandler(AbstractEventHandler):
    def handle_event(self, event: dict):
        before = event["before"]
        after = event["after"]
        event = Event(
            source= 'ticket-command',
            op= 'u',
            payload= after
        )
        producer.send_message('tickets', event)

class DeleteEventHandler(AbstractEventHandler):
    def handle_event(self, event: dict):
        deleted_data = event["before"]
        event = Event(
            source= 'ticket-command',
            op= 'd',
            payload= deleted_data
        )
        producer.send_message('tickets', event)

class HighlightEventHandler(AbstractEventHandler):
    def handle_event(self, event: dict):
        return super().handle_event(event)

class SummarizeEventHandler(AbstractEventHandler):
    def handle_event(self, event: dict):
        return super().handle_event(event)
    
class TagEventHandler(AbstractEventHandler):
    def handle_event(self, event: dict):
        return super().handle_event(event)
        
class EventProcessor:
    def __init__(self):
        self.handlers = {
            "c": InsertEventHandler(),
            "u": UpdateEventHandler(),
            "d": DeleteEventHandler(),
            "h": HighlightEventHandler(),
            "s": SummarizeEventHandler(),
            "t": TagEventHandler()
        }

    def process_event(self, event: dict):
        op = event.get("op")
        handler = self.handlers.get(op)

        if handler:
            handler.handle_event(event)
        else:
            print(f"[UNKNOWN] Event received: {event}")