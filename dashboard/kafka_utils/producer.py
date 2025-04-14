from confluent_kafka import Producer
import json
from abc import ABC, abstractmethod
from .event import Event

class AbstractProducer(ABC):
    @abstractmethod
    def send_event(self, topic: str, key: str, message: str):
        pass

class KafkaProducerService(AbstractProducer):
    def __init__(self, config: dict):
        self.producer = Producer(config)

    def send_event(self, topic: str, event: Event):
        """Gửi event đến Kafka topic"""
        try:
            event.validate()
            
            event_dict = event.to_dict()
            
            key = str(event.id)
            
            self.producer.produce(
                topic,
                key=key.encode("utf-8"),
                value=json.dumps(event_dict).encode("utf-8"),
                callback=self.delivery_report
            )
            
        except Exception as e:
            print(f"[ERROR] Failed to send event: {e}")
            raise e

import os
from dotenv import load_dotenv
load_dotenv()

producer = KafkaProducerService({
    'bootstrap.servers': os.getenv("KAFKA_BROKERS_INTERNAL"),
    'client.id': "dashboard_service",
    'acks': 'all',
    'retries': 3,
    'retry.backoff.ms': 100,
})

import datetime
def send_to_dlq(event, error_message, retry_count=0):
    dlq_payload = {
        "original_event": event.to_dict(),
        "error_message": str(error_message),
        "timestamp": datetime.utcnow().isoformat(),
        "retry_count": retry_count + 1,
    }
    producer.produce("dashboard-dlq", json.dumps(dlq_payload).encode("utf-8"))
    producer.flush()
    print(f"[DLQ] Event sent to DLQ due to error: {error_message}")