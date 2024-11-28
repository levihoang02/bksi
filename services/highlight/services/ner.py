import json
from utils.config import Config
from confluent_kafka import Consumer, Producer, KafkaException
from services.processing import process_data


config = Config()

def create_consumer():
    return Consumer({
        'bootstrap.servers': config.KAFKA_BROKERS_EXTERNAL,
        'group.id': config.KAFKA_GROUP_ID,
        'auto.offset.reset': 'latest'
    })

def create_producer():
    return Producer({'bootstrap.servers': config.KAFKA_BROKERS_EXTERNAL,
                     'compression.type': 'lz4'
                    })

def run_service():
    consumer = create_consumer()
    producer = create_producer()

    consumer.subscribe([config.KAFKA_REQUEST_TOPIC])
    print(f"Subscribed to topic: {config.KAFKA_REQUEST_TOPIC}")

    try:
        while True:
            # Poll messages from Kafka
            msg = consumer.poll(1.0)

            if (msg is None or msg == {}):
                continue
            if msg.error():
                print(f"Consumer error: {msg.error()}")
                continue

            # Deserialize message
            data = json.loads(msg.value().decode('utf-8'))
            print(f"Received message: {data}")
            user_id = data.get('user_id', 'unknown')
            # Process the data
            result = process_data(data)
            print(result)
            processed_data = {
                "user_id": user_id,
                "value": result
            }
            # Produce the processed data to the output topic
            producer.produce(
                config.KAFKA_RESPONSE_TOPIC,
                value=json.dumps(processed_data).encode('utf-8'),
                callback=lambda err, msg: print(f"Delivered to {msg.topic()} [{msg.partition()}]" if not err else f"Failed: {err}")
            )
            producer.flush()

    except KeyboardInterrupt:
        print("Shutting down service...")
        consumer.close()
    except Exception as e:
        print(e)
        consumer.close()
    finally:
        consumer.close()



