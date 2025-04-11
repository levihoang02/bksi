from flask import Flask, Response, request
from flask_cors import CORS
from routes.feedback_routes import feedback_bp
from utils.config import Config
from prometheus_metrics import REQUEST_COUNT, REQUEST_LATENCY, get_metrics, system_monitor
import time

def create_app():
    app = Flask(__name__)
    CORS(app)
    
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
    
    app.register_blueprint(feedback_bp)
    
    return app

app = create_app()

if __name__ == '__main__':
    # Start the system metrics monitor before running the app
    system_monitor.start()
    app.run(debug=True, host='0.0.0.0', port=5000)