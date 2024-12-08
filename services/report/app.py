from flask import Flask, request, jsonify
import threading
from services.consumer import run_service
from utils.config import Config
import time
import logging
from logging.handlers import RotatingFileHandler

config = Config()

app = Flask(__name__)
def setup_logger():
    # Create logs directory if it doesn't exist
    import os
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Configure file handler
    file_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=1024 * 1024,  # 1MB
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Application startup')

def start_consumer():
    max_retries = 5
    retry_count = 0
    base_delay = 1  # Starting delay in seconds
    
    while retry_count < max_retries:
        try:
            run_service()
            break  # If successful, exit the loop
        except Exception as e:
            retry_count += 1
            app.logger.error(f"Consumer service failed (attempt {retry_count}/{max_retries}): {str(e)}")
            
            if retry_count >= max_retries:
                app.logger.critical("Maximum retry attempts reached. Consumer service has failed permanently.")
                break
                
            # Exponential backoff: 1s, 2s, 4s, 8s, 16s
            delay = base_delay * (2 ** (retry_count - 1))
            app.logger.info(f"Waiting {delay} seconds before retry...")
            time.sleep(delay)

@app.route('/health', methods=['GET'])
def health_check():
    health_status = {
        "status": "healthy" if 'consumer_thread' in globals() and consumer_thread.is_alive() else "unhealthy",
        "service": "report-service",
        "consumer_thread": {
            "active": consumer_thread.is_alive() if 'consumer_thread' in globals() else False,
        },
         "timestamp": time.time()
    }
    
    return jsonify(health_status), 200 if health_status["status"] == "healthy" else 503

if __name__ == "__main__":
    setup_logger()
    # Make the thread daemon so it exits when the main program exits
    consumer_thread = threading.Thread(target=start_consumer, daemon=True)
    consumer_thread.start()
    
    app.run(
        host='0.0.0.0',
        port=5100,
        debug=True
    )