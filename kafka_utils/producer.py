from confluent_kafka import Producer
from retry import retry
import json
from abc import ABC, abstractmethod

class AbstractProducer(ABC):
    @abstractmethod
    def send_message(self, topic: str, key: str, message: str):
        pass

class KafkaProducerService(AbstractProducer):
    def __init__(self, config: dict):
        self.producer = Producer(config)

    def delivery_report(self, err, msg):
        if err is not None:
            print(f"[ERROR] Message delivery failed: {err}")
        else:
            print(f"[INFO] Message delivered to {msg.topic()} [{msg.partition()}]")

    @retry(tries=3, delay=2, backoff=2, exceptions=(Exception,))
    def send_message(self, topic: str, key: str, message: str):
        try:
            self.producer.produce(
                topic,
                key=key.encode("utf-8"),
                value=json.dumps(message).encode("utf-8"),
                callback=self.delivery_report
            )
            self.producer.flush()
        except Exception as e:
            print(f"[ERROR] Failed to send message: {e}")
            raise e

    def close(self):
        self.producer.flush()