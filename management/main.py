from dotenv import load_dotenv
load_dotenv()

from models.database import db
from flask import Flask, Response, request
from routes import service_bp
from prometheus_metrics import get_metrics, system_monitor

app = Flask(__name__)
app.register_blueprint(service_bp)

@app.route('/metrics')
def metrics():
    return Response(get_metrics()[0], mimetype=get_metrics()[1])

def initialize_background_tasks():
    db.create_all()
    system_monitor.start()

initialize_background_tasks()