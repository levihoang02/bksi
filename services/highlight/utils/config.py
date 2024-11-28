import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    KAFKA_BROKERS_INTERNAL = os.getenv("KAFKA_BROKERS_INTERNAL")
    KAFKA_BROKERS_EXTERNAL = os.getenv("KAFKA_BROKERS_EXTERNAL")
    KAKFKA_CONSUMER_GROUP = os.getenv("KAFKA_CONSUMER_GROUP")
    KAFKA_REQUEST_TOPIC = os.getenv("KAFKA_REQUEST_TOPIC")
    KAFKA_RESPONSE_TOPIC = os.getenv("KAFKA_RESPONSE_TOPIC")
    KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID")