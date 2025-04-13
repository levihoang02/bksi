from dotenv import load_dotenv
load_dotenv()

from models.database import db
from flask import Flask, Response, request
from routes import service_bp
from prometheus_metrics import REQUEST_COUNT, REQUEST_LATENCY, get_metrics, system_monitor
import time

app = Flask(__name__)
app.register_blueprint(service_bp)

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    if request.path != '/metrics':  # Don't track metrics endpoint
        latency = time.time() - request.start_time
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.path,
            status=response.status_code
        ).inc()
        REQUEST_LATENCY.labels(
            method=request.method,
            endpoint=request.path
        ).observe(latency)
    return response

@app.route('/metrics')
def metrics():
    return Response(get_metrics()[0], mimetype=get_metrics()[1])

def initialize_background_tasks():
    db.create_all()
    system_monitor.start()


if __name__ == "__main__":
    initialize_background_tasks()
    app.run(host='0.0.0.0', port=3200, debug= True)