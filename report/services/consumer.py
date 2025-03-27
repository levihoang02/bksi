import json
import logging
from utils.config import Config
from confluent_kafka import Consumer, Producer, KafkaException
from schemas.report import add_report

config = Config()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_consumer():
    return Consumer({
        'bootstrap.servers': config.KAFKA_BROKERS_EXTERNAL,
        'group.id': config.KAFKA_GROUP_ID,
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': False  # Disable auto commit for better control
    })

def create_producer():
    return Producer({'bootstrap.servers': config.KAFKA_BROKERS_EXTERNAL,
                     'compression.type': 'lz4'
                    })

def run_service():
    consumer = create_consumer()
    consumer.subscribe([config.KAFKA_REPORT_TOPIC])
    logger.info(f"Subscribed to topic: {config.KAFKA_REPORT_TOPIC}")

    try:
        while True:
            msg = consumer.poll(1.0)

            if msg is None:
                continue
            if msg.error():
                logger.error(f"Consumer error: {msg.error()}")
                continue

            try:
                # Deserialize message
                data = json.loads(msg.value().decode('utf-8'))
                
                # Validate required fields
                required_fields = ['service', 'status', 'timestamp']
                if not all(field in data for field in required_fields):
                    logger.error(f"Missing required fields in message: {data}")
                    consumer.commit(msg)
                    continue

                # Extract data
                service_name = data['service']
                status = data['status']
                timestamp = data['timestamp']
                
                # Add the new report to the database
                add_report(service_name, timestamp, status)
                logger.info(f"New report created: Service: {service_name}, Status: {status}, Timestamp: {timestamp}")
                
                # Commit the message after successful processing
                consumer.commit(msg)

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse message: {e}")
                consumer.commit(msg)
            except Exception as e:
                logger.error(f"Error processing message: {e}")

    except KeyboardInterrupt:
        logger.info("Shutting down service...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        consumer.close()