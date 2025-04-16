from abc import ABC, abstractmethod
from kafka_utils.event import Event, EventType
from kafka_utils.producer import producer, send_to_dlq
from utils.config import Config
from helpers.html import decode_html
from database.mongo import mongo
from models.ticket import Ticket

config = Config()

class AbstractEventHandler(ABC):
    @abstractmethod
    def handle_event(self, event: Event):
        pass
    
class InsertEventHandler(AbstractEventHandler):
    def handle_event(self, event: Event):
        new_data = event.to_dict()
        payload = new_data.get("payload")
        if(payload.get("created_by") == "customer"):
            raw_content = decode_html(payload.get("message"))
            new_payload = {
                "ticket_id": payload.get("id"),
                "content":  raw_content
            }
            new_event = Event(
                    source='management', 
                    op=EventType.CREATE,
                    payload= new_payload
                )
            ticket = Ticket(id= payload.get("id"), content= raw_content)
            data = ticket.to_dict()
            mongo.insert_one(collection_name= 'tickets', data=data)
            producer.send_event('tickets', key=str(new_data["id"]), event= new_event)
            
class NerEventHandler(AbstractEventHandler):
    def handle_event(self, event: Event):
        data = event.to_dict()
        mongo.update_one(collection_name= 'tickets', query= {'id': data.get('id')}, update_values= {'ner': data.get('value')})
        
class SumEventHandler(AbstractEventHandler):
    def handle_event(self, event: Event):
        data = event.payload
        mongo.update_one(collection_name= 'tickets', query= {'id': data.get('id')}, update_values= {'summary': data.get('value')})

class TagEventHandler(AbstractEventHandler):
    def handle_event(self, event: Event):
        data = event.payload
        mongo.update_one(collection_name= 'tickets', query= {'id': data.get('id')}, update_values= {'tags': data.get('value')})

class DeleteEventHandler(AbstractEventHandler):
    def handle_event(self, event: Event):
        data = event.payload
        mongo.delete_one(collection_name= 'tickets', query= {'id': data.get('id')})
        
class EventProcessor:
    def __init__(self):
        self.handlers = {
            EventType.CREATE: InsertEventHandler,
            EventType.NER: NerEventHandler,
            EventType.DELETE: DeleteEventHandler,
            EventType.SUMMARIZE: SumEventHandler,
            EventType.TAG: TagEventHandler,
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
                send_to_dlq(event= event, error_message= e)
        else:
            print(f"[UNKNOWN] Event received: {event}")