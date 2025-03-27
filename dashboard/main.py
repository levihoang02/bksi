import signal
import sys
import json

from utils.config import Config
from kafka_utils.consumer import KafkaConsumerService
from handlers.process import process_message

config = Config()

message_consumer = KafkaConsumerService(config.KAFKA_REPORT_TOPIC, config.KAFKA_GROUP_ID, config.KAFKA_BROKERS_INTERNAL)

def shutdown_handler(signal, frame):
    print("\nShutting down gracefully...")
    message_consumer._close()
    sys.exit(0)

signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)


if __name__ == "__main__":
    print("Dashboard Service Start!")
    message_consumer.consume_messages(process_message)
    # while(True):
    #    print("Hello")
    