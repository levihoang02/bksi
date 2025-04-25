print("=== SERVICE STARTING ===")

import signal
import sys
import threading
from typing import Dict, Any
from flask import Flask, Response
from utils.config import Config
from kafka_utils.consumer import KafkaConsumerService, create_topic_configs, seed_topics
from kafka_utils.dlq_consumer import DLQConsumer
from kafka_utils.event import Event, debezium_to_event
from handlers.bksi import EventProcessor
from prometheus_metrics import (
    REQUEST_COUNT, REQUEST_LATENCY, get_metrics, system_monitor
)
from database.mongo import mongo
from routes.ticket import ticket_bp

config = Config()

topic_configs = create_topic_configs(config.KAFKA_CONSUME_TOPIC, config.DLQ_TOPIC)
futures = seed_topics(brokers= config.KAFKA_BROKERS_INTERNAL, topic_configs=topic_configs)


message_consumer = KafkaConsumerService(config.KAFKA_CONSUME_TOPIC, config.KAFKA_GROUP_ID, config.KAFKA_BROKERS_INTERNAL)
dlq_consumer = DLQConsumer(config.DLQ_TOPIC, config.KAFKA_GROUP_ID, config.KAFKA_BROKERS_INTERNAL)
processor = EventProcessor()

# Create Flask app for metrics
app = Flask(__name__)
app.register_blueprint(ticket_bp)

@app.route('/metrics')
def metrics():
    return Response(get_metrics()[0], mimetype=get_metrics()[1])


def shutdown_handler(signal, frame):
    print("\nShutting down gracefully...")
    message_consumer._close()
    mongo.close_connection()
    sys.exit(0)

signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)

def process_func(msg_data: Dict[str, Any]):
    try:
        # If the message comes from Debezium (check for specific Debezium fields)
        if "before" in msg_data and "after" in msg_data:
            event = debezium_to_event(msg_data)
        else:
            # Otherwise, assume it's a regular event
            event = Event.from_dict(msg_data)

        # Validate the event
        if event.validate():
            processor.process_event(event)

    except Exception as e:
        print(f"Error processing event: {e}")
    finally:
        pass

def run_metrics_server():
    app.run(host="0.0.0.0", port=config.PORT if config.PORT else 8000)
    
def run_kafka_consumer():
    message_consumer.consume_messages(process_func)
    
def run_dlq_consumer():
    dlq_consumer.consume_dlq(process_func)
    



def initialize_background_tasks():
    print("Dashboard Service Start!")
    system_monitor.start()

    consumer_thread = threading.Thread(target=run_kafka_consumer, daemon=True)
    consumer_thread.start()
    
    consumer_thread = threading.Thread(target=run_dlq_consumer, daemon= True)
    consumer_thread.start()
    
initialize_background_tasks()