import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    KAFKA_BROKERS_INTERNAL = os.getenv("KAFKA_BROKERS_INTERNAL")
    KAFKA_BROKERS_EXTERNAL = os.getenv("KAFKA_BROKERS_EXTERNAL")
    CONSUMER_TOPIC = os.getenv("CONSUMER_TOPIC")
    PRODUCER_TOPIC = os.getenv("PRODUCER_TOPIC")
    ENABLE_EVENT_DRIVEN = os.getenv("ENABLE_EVENT_DRIVEN")
    PORT = os.getenv("PORT")