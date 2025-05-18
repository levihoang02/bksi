import os
from dotenv import load_dotenv
from typing import List
load_dotenv()

class Config:
    KAFKA_BROKERS_INTERNAL = os.getenv("KAFKA_BROKERS_INTERNAL")
    KAFKA_BROKERS_EXTERNAL = os.getenv("KAFKA_BROKERS_EXTERNAL")
    KAFKA_CONSUMER_GROUP = os.getenv("KAFKA_CONSUMER_GROUP")
    KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID")
    MONGO_URI = os.getenv("MONGO_URI")
    MONGODB_DATABASE = os.getenv("MONGODB_DATABASE")  
    MONGODB_COLLECTION = os.getenv("MONGODB_COLLECTION")
    PORT = os.getenv("PORT")
    DLQ_TOPIC = os.getenv("DLQ_TOPIC")
    KAFKA_CONSUME_TOPIC = None
    GATE_WAY = os.getenv("GATE_WAY")
    API_KEY = os.getenv("API_KEY")
    @classmethod
    def get_kafka_topics(cls):
        topics_raw = os.getenv("KAFKA_CONSUME_TOPIC", "")
        return [t.strip() for t in topics_raw.split(",") if t.strip()]

Config.KAFKA_CONSUME_TOPIC = Config.get_kafka_topics()
