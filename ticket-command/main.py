from confluent_kafka import Consumer, KafkaException
import signal
import sys
import json

from utils.config import Config
from models.event import Event
from process import process_event, mongo

config = Config()

TOPIC = config.KAFKA_TOPIC

message_consumer = Consumer({
        'bootstrap.servers': config.KAFKA_BROKERS_EXTERNAL,
        'group.id': config.KAFKA_GROUP_ID,
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': False  # Disable auto commit for better control
    })

message_consumer.subscribe([TOPIC])

def shutdown_handler(signal, frame):
    print("\nShutting down gracefully...")
    message_consumer.close()
    mongo.close()
    sys.exit(0)

signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)

def consume_messages():
    print(f"Consuming messages from Kafka topic: {TOPIC}...")
    while True:
        try:
            msg = message_consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                print(f"Kafka error: {msg.error()}")
                continue
            try:
                message_data = json.loads(msg.value().decode("utf-8"))
                event = Event(**message_data)
                print(f"Received Event: {event}")

                process_event(event)

                message_consumer.commit(msg)
            
            except json.JSONDecodeError:
                print("Received invalid JSON data")
            except Exception as e:
                print(f"Error processing message: {e}")

        except KafkaException as e:
            print(f"Kafka Consumer Error: {e}")
        except Exception as e:
            print(f"Unexpected Error: {e}")
    
if __name__ == "__main__":
    consume_messages()
 

