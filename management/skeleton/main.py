import threading
import uvicorn
import sys
import signal
from modules.http_handler import app
from modules.MB_handler import EventHandlerService
from utils.config import Config
from modules.processor.process import process

config = Config()

APP_PORT = int(config.PORT)

event_handler = EventHandlerService(consumer_topics=config.CONSUMER_TOPIC, 
                                    producer_topic=config.PRODUCER_TOPIC, 
                                    group_id='highlight-consumer-group', 
                                    servers=config.KAFKA_BROKERS_INTERNAL) if (config.ENABLE_EVENT_DRIVEN == 'true') else None

def shutdown_handler(signal, frame):
    print("\nShutting down gracefully...")
    event_handler._close()
    sys.exit(0)

signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)

if __name__ == "__main__":
    if(config.ENABLE_EVENT_DRIVEN == 'true'):
        kafka_thread = threading.Thread(target=event_handler.consume_messages, args=(process,), daemon=True)
        kafka_thread.start()
    
    uvicorn.run(app, host="0.0.0.0", port=APP_PORT)