import json
import requests
from abc import ABC, abstractmethod
from utils.config import Config
from kafka_utils.event import Event, EventType

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

def reload_prometheus():
    try:
        response = requests.post(PROMETHEUS_URL)
        response.raise_for_status()
        print("Prometheus reloaded successfully")
    except requests.exceptions.RequestException as e:
        print(f"Failed to reload Prometheus: {e}")

class AbstractEventHandler(ABC):
    @abstractmethod
    def handle_event(self, event: Event):
        pass

class InsertEventHandler(AbstractEventHandler):
    def handle_event(self, event: Event):
        print(f"Processing CREATE event: {event}")
        data = event.payload
        
        try:
            targets = load_targets()
            
            # Tạo target mới
            target = f"{data['host']}:{data['port']}"
            new_entry = {
                "targets": [target],
                "labels": {"job": data['job']}
            }
            
            targets.append(new_entry)
            
            save_targets(targets)
            print(f"Added new target: {target} for job: {data['job']}")
            
            reload_prometheus()
            
        except Exception as e:
            print(f"Error handling CREATE event: {e}")

class UpdateEventHandler(AbstractEventHandler):
    def handle_event(self, event: Event):
        print(f"Processing UPDATE event: {event}")
        data = event.payload
        
        try:
            targets = load_targets()
            # Implement update logic
            new_target = f"{data['host']}:{data['port']}"
            job_name = data['job']
            target_found = False
            for target in targets:
                if target['labels']['job'] == job_name:
                    target['targets'] = [new_target]
                    target_found = True
                    print(f"Updated target for job {job_name} to {new_target}")
                    break
            if target_found:
                save_targets(targets)
                reload_prometheus()
            else:
                print(f"No matching target found for update")
        except Exception as e:
            print(f"Error handling UPDATE event: {e}")

class DeleteEventHandler(AbstractEventHandler):
    def handle_event(self, event: Event):
        print(f"Processing DELETE event: {event}")
        data = event.payload
        
        try:
            targets = load_targets()
            print(f"Current targets before deletion: {json.dumps(targets, indent=2)}")
            
            target_to_delete = f"{data['host']}:{data['port']}"
            job_name = data['job']
            
            updated_targets = []
            deleted = False
            
            for target in targets:
                should_delete = False
            
                if (target['labels']['job'] == job_name and 
                    target_to_delete in target['targets']):
                    should_delete = True
                
                if should_delete:
                    deleted = True
                    print(f"Removing target {target_to_delete} for job {job_name}")
                    continue
                    
                updated_targets.append(target)
            
            if deleted:
                save_targets(updated_targets)
                print(f"Updated targets after deletion: {json.dumps(updated_targets, indent=2)}")
                reload_prometheus()
            else:
                print(f"No matching target found for deletion")
            
        except Exception as e:
            print(f"Error handling DELETE event: {e}")
            raise e

class EventProcessor:
    def __init__(self):
        self.handlers = {
            EventType.CREATE: InsertEventHandler,
            EventType.DELETE: DeleteEventHandler,
            EventType.UPDATE: UpdateEventHandler,
        }

    def process_event(self, event: Event):
        print(f"Processing event type: {event.op}")
        
        handler_class = self.handlers.get(event.op)
        if handler_class:
            try:
                handler = handler_class()
                handler.handle_event(event)
                print(f"Successfully processed {event.op} event")
            except Exception as e:
                print(f"Error processing event: {e}")
        else:
            print(f"[UNKNOWN] Event received: {event}")