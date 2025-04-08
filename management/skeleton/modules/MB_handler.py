from confluent_kafka import Consumer, KafkaException, Producer
import json
import threading
from retry import retry

class EventHandlerService:
    def __init__(self, consumer_topics, producer_topic, group_id=None, servers=None):
        print("Initializing message broker reader/sender...")
        self.running = True
        self.lock = threading.Lock()
        self.consumer_topics = consumer_topics
        self.producer_topic = producer_topic
        self.group_id = group_id
        self.servers = servers

        self.consumer_config = {
            'bootstrap.servers': self.servers,
            'group.id': self.group_id,
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': False  # Disable auto commit for better control
        }
        self.producer_config = {
            'bootstrap.servers': self.servers,
        }
        self.consumer = Consumer(self.consumer_config)
        self.producer = Producer(self.producer_config)
        if isinstance(self.consumer_topics, str):
            self.consumer.subscribe([self.consumer_topics])
        elif isinstance(self.consumer_topics, list):
            self.consumer.subscribe(self.consumer_topics)
        print("Event driven protocal initalize successfully")

    def consume_messages(self, process_function):
        """ Continuously consume messages and apply a processing function """
        try:
            while self.running:
                msg = self.consumer.poll(timeout=1.0)
                    
                if msg is None:
                        continue
                if msg.error():
                    print(f"Consumer error: {msg.error()}")
                    continue
                    
                try:
                    # Decode bytes to string and parse JSON
                    message_str = msg.value().decode("utf-8")
                    message_data = json.loads(message_str)
                    key = message_data['id']
                    payload = message_data['payload']
                    # Process the parsed message using the provided function
                    result = process_function(payload)
                    self.consumer.commit(msg)
                    self.send_message(self.producer_topic, key=str(key), message=result)
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}")
                    continue
        except KeyboardInterrupt:
            print("Stopping consumer...")

        finally:
            self.consumer.close()
            
    @retry(tries=3, delay=2, backoff=2, exceptions=(Exception,))
    def send_message(self, topic, key: str, message: str):
        try:
            self.producer.produce(
                topic,
                key=key.encode("utf-8"),
                value=json.dumps(message).encode("utf-8"),
                callback=self.delivery_report
            )
            self.producer.flush()
        except Exception as e:
            print(f"[ERROR] Failed to send message: {e}")
            raise e
        
    def delivery_report(self, err, msg):
        if err is not None:
            print(f"[ERROR] Message delivery failed: {err}")
        else:
            print(f"[INFO] Message delivered to {msg.topic()} [{msg.partition()}]")
            
    def _close(self):
        self.running = False
        self.consumer.close()
        self.producer.flush()