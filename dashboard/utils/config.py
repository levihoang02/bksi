import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    KAFKA_BROKERS_INTERNAL = os.getenv("KAFKA_BROKERS_INTERNAL")
    KAFKA_BROKERS_EXTERNAL = os.getenv("KAFKA_BROKERS_EXTERNAL")
    KAFKA_CONSUMER_GROUP = os.getenv("KAFKA_CONSUMER_GROUP")
    KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID")
    KAFKA_CONSUME_TOPIC = os.getenv("KAFKA_CONSUME_TOPIC")
    PROMETHEUS_HOST = os.getenv("PROMETHEUS_HOST")
    MONGO_URI =  os.getenv('MONGO_URI')
    DLQ_TOPIC = os.getenv('DLQ_TOPIC')