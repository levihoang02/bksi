from confluent_kafka import Consumer, KafkaException
import json
import time
from kafka_utils.event import Event
from kafka_utils.producer import send_to_dlq

MAX_RETRIES = 3
RETRY_BACKOFF_BASE_SECONDS = 2

class DLQConsumer:
    def __init__(self, topic, group_id, bootstrap_servers):
        self.topic = topic
        self.group_id = group_id
        self.bootstrap_servers = bootstrap_servers

        self.config = {
            'bootstrap.servers': self.bootstrap_servers,
            'group.id': self.group_id,
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': False
        }

        self.consumer = Consumer(self.config)
        self.consumer.subscribe([self.topic])

    def consume_dlq(self, process_func):
        print(f"[DLQConsumer] Subscribed to DLQ topic: {self.topic}")
        try:
            while True:
                msg = self.consumer.poll(timeout=1.0)
                if msg is None:
                    continue
                if msg.error():
                    print(f"[DLQConsumer] Error: {msg.error()}")
                    continue

                try:
                    message_str = msg.value().decode("utf-8")
                    dlq_event = json.loads(message_str)
                    event_data = dlq_event.get("original_event")
                    retry_count = dlq_event.get("retry_count", 0)

                    if not event_data:
                        print("[DLQConsumer] No original_event field, skipping.")
                        continue

                    if retry_count >= MAX_RETRIES:
                        print(f"[DLQConsumer] Max retries exceeded for event: {event_data}")
                        self.consumer.commit(msg)
                        continue

                    print(f"[DLQConsumer] Retrying event (Attempt #{retry_count + 1}): {event_data}")

                    try:
                        process_func(event_data)
                        print("[DLQConsumer] Event processed successfully.")
                        self.consumer.commit(msg)
                    except Exception as process_error:
                        print(f"[DLQConsumer] Retry failed again: {process_error}")
                        event = Event.from_dict(event_data)
                        send_to_dlq(event, str(process_error), retry_count)
                        time.sleep(RETRY_BACKOFF_BASE_SECONDS ** retry_count)

                except Exception as e:
                    print(f"[DLQConsumer] Error processing message: {e}")
        except KeyboardInterrupt:
            print("[DLQConsumer] Stopped by user.")
        finally:
            self.consumer.close()

    def close(self):
        self.consumer.close()
