import json
import requests
import json

from models.event import Event, EVENT_TYPES
from utils.config import Config

config = Config()

TARGETS_FILE = "/etc/prometheus/targets/targets.json"
PROMETHEUS_URL = f"http://{config.PROMETHEUS_HOST}/-/reload"



def load_targets():
    try:
        with open(TARGETS_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_targets(targets):
    with open(TARGETS_FILE, "w") as file:
        json.dump(targets, file, indent=2)

def add_service(data):
    print(f"Received new service: {data}")
    
    targets = load_targets()
    
    target = f"{data['host']}:{data['port']}"
    new_entry = {"targets": [target], "labels": {"job": data["name"]}}
    targets.append(new_entry)
    save_targets(targets)

    print("Updated targets.json")

    # Gửi request reload Prometheus
    try:
        requests.post(PROMETHEUS_URL)
        print("Prometheus reloaded successfully")
    except requests.exceptions.RequestException as e:
        print(f"Failed to reload Prometheus: {e}")

def process_message(message: Event):
    if(message["type"] == EVENT_TYPES["NEW_SERVICE"]):
        return add_service(message["payload"])