import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    KAFKA_BROKERS_INTERNAL = os.getenv("KAFKA_BROKERS_INTERNAL")
    KAFKA_BROKERS_EXTERNAL = os.getenv("KAFKA_BROKERS_EXTERNAL")
    KAFKA_CONSUMER_GROUP = os.getenv("KAFKA_CONSUMER_GROUP")
    KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID")
    KAFKA_CONSUME_TOPIC = os.getenv("KAFKA_CONSUME_TOPIC")
    MONGODB_HOST = os.getenv("MONGODB_HOST")
    MONGODB_PORT = os.getenv("MONGODB_PORT")  
    MONGODB_DATABASE = os.getenv("MONGODB_DATABASE")  
    MONGODB_COLLECTION = os.getenv("MONGODB_COLLECTION")
    DB_USERNAME = os.getenv("DB_USERNAME")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    PORT = os.getenv("PORT")
    DLQ_TOPIC = os.getenv("DLQ_TOPIC")