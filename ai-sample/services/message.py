import threading
from services.producer import producer
from services.event import Event

def async_publish_event(topic: str, event: Event):
    """Publish an event asynchronously without blocking."""
    def _publish():
        try:
            producer.send_event(topic, event)
            print(f"[Kafka] Async published event: {event.id}")
        except Exception as e:
            print(f"[Kafka] Failed async publish: {e}")
    
    threading.Thread(target=_publish, daemon=True).start()