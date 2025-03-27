import signal
import sys
import json
from handlers.handler import EventProcessor
from kafka_utils.consumer import KafkaConsumerService
from utils.config import Config

config = Config()

message_consumer = KafkaConsumerService(config.KAFKA_TOPIC, config.KAFKA_GROUP_ID, config.KAFKA_BROKERS_INTERNAL)

processor = EventProcessor()

def shutdown_handler(signal, frame):
    print("\nShutting down gracefully...")
    message_consumer._close()
    sys.exit(0)

signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)


if __name__ == "__main__":
    message_consumer.consume_messages(processor.process_event)

