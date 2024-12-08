from utils.config import Config
from confluent_kafka import Producer
import logging
import json

logger = logging.getLogger(__name__)

config = Config()

def create_producer():
    return Producer({'bootstrap.servers': config.KAFKA_BROKERS_EXTERNAL,
                     'compression.type': 'lz4'})
    
def send_report(data):
    producer = create_producer()
    producer.produce(config.KAFKA_REPORT_TOPIC, value=json.dumps(data))
    producer.flush()
