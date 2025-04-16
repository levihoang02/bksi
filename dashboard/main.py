print("=== SERVICE STARTING ===")

import signal
import sys
import threading
from flask import Flask, Response, request, jsonify
from utils.config import Config
from kafka_utils.consumer import KafkaConsumerService
from kafka_utils.dlq_consumer import DLQConsumer
from kafka_utils.event import Event
from handlers.manage import EventProcessor
from prometheus_metrics import (
    REQUEST_COUNT, REQUEST_LATENCY, get_metrics, system_monitor
)
from services.metric_service import metric_service, seed_metrics_from_json
from models.metric import Metric

METRICS_FILE_PATH = 'data/metrics.json'

config = Config()
message_consumer = KafkaConsumerService(config.KAFKA_CONSUME_TOPIC, config.KAFKA_GROUP_ID, config.KAFKA_BROKERS_INTERNAL)
dlq_consumer = DLQConsumer(config.DLQ_TOPIC, config.KAFKA_GROUP_ID, config.KAFKA_BROKERS_INTERNAL)
processor = EventProcessor()

# Create Flask app for metrics
app = Flask(__name__)

@app.route('/metrics')
def metrics():
    return Response(get_metrics()[0], mimetype=get_metrics()[1])

@app.route('/metric', methods=['POST'])
def create_new_metric():
    data = request.json
    metric = Metric(
        metric_name=data['metric_name'],
        chart_type=data['chart_type'],
        desc= data['desc']
    )
    metric_service.save_metric(metric= metric)
    return jsonify({'message': 'Metric created successfully'}), 201

@app.route('/metric/<name>', methods=['DELETE'])
def delete_metric(name):
    response = metric_service.delete_metric(name)
    return response

    
def shutdown_handler(signal, frame):
    print("\nShutting down gracefully...")
    message_consumer._close()
    sys.exit(0)

signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)

def process_func(msg_data):
    try:
        event = Event.from_dict(msg_data)
        processor.process_event(event)
    except Exception as e:
        print(e)
    finally:
        pass

def run_metrics_server():
    app.run(host="0.0.0.0", port=8080)
    
def run_kafka_consumer():
    message_consumer.consume_messages(process_func)
    
def run_dlq_consumer():
    dlq_consumer.consume_dlq(process_func)

def initialize_background_tasks():
    print("Dashboard Service Start!")
    seed_metrics_from_json(file_path= METRICS_FILE_PATH)
    system_monitor.start()
    
    consumer_thread = threading.Thread(target=run_kafka_consumer)
    consumer_thread.start()
    
    dlq_thread = threading.Thread(target= run_dlq_consumer)
    dlq_thread.start()
    
initialize_background_tasks()