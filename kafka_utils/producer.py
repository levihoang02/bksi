from confluent_kafka import Producer
from retry import retry
import json
    
class ProducerService:
    def __init__(self, config) -> None:
        self.producer = Producer(config)
        
    def delivery_report(self, err, msg):
        """ Called once for each message produced to indicate delivery result"""
        if err is not None:
            print(f'Message delivery failed: {err}')
        else:
            print(f'Message delivered to {msg.topic()} [{msg.partition()}]')
    
    # @retry(tries=3, delay=2, backoff=2, exceptions=(Exception,))
    def send_message(self, topic, key, message):
           try:
               # Use ensure_ascii=False to keep the original text
               self.producer.produce(
                   topic,
                   key=key,
                   value=message,
                   callback=self.delivery_report
               )
               self.producer.flush()
           except Exception as e:
               print(f"Failed to send message: {e}")
        
    def _disconnect(self):
        self.producer.flush()