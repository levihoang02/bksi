print("=== SERVICE STARTING ===")

import signal
import sys
import threading
import time
from flask import Flask, Response
from utils.config import Config
from kafka_utils.consumer import KafkaConsumerService
from kafka_utils.event import Event
from handlers.bksi import EventProcessor
from prometheus_metrics import (
    REQUEST_COUNT, REQUEST_LATENCY, get_metrics, system_monitor
)
from database.mongo import mongo
from routes.ticket import ticket_bp

config = Config()
message_consumer = KafkaConsumerService(config.KAFKA_CONSUME_TOPIC, config.KAFKA_GROUP_ID, config.KAFKA_BROKERS_INTERNAL)
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

def process_func(msg_data):
    start_time = time.time()
    try:
        event = Event.from_dict(msg_data)
        processor.process_event(event)
    except Exception as e:
        raise e
    finally:
        pass

def run_metrics_server():
    app.run(host="0.0.0.0", port=config.PORT if config.PORT else 8000)
    
def run_kafka_consumer():
    message_consumer.consume_messages(process_func)

if __name__ == "__main__":
    print("Dashboard Service Start!")
    
    system_monitor.start()
    
    consumer_thread = threading.Thread(target=run_kafka_consumer)
    consumer_thread.start()
    
    app.run(host="0.0.0.0", port= int(config.PORT) if config.PORT else 8080)