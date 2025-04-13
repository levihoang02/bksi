from abc import ABC, abstractmethod
from kafka_utils.event import Event, EventType
from kafka_utils.producer import KafkaProducerService
from utils.config import Config
from helpers.html import decode_html
from database.mongo import mongo
from models.ticket import Ticket

config = Config()

producer_config = {
        "bootstrap.servers": config.KAFKA_BROKERS_INTERNAL,
        "client.id": "ticket-producer",
        "acks": "all"
}

producer = KafkaProducerService(producer_config)

class AbstractEventHandler(ABC):
    @abstractmethod
    def handle_event(self, event: Event):
        pass
    
class InsertEventHandler(AbstractEventHandler):
    def handle_event(self, event: Event):
        new_data = event["after"]
        if(new_data["created_by"] == "customer"):
            raw_content = decode_html(new_data["message"])
            payload = {
                "ticket_id": new_data["id"],
                "content":  raw_content
            }
            new_event = Event(
                    source='management', 
                    op=EventType.CREATE,
                    payload= payload
                )
            ticket = Ticket(id= new_data["id"], content= raw_content)
            data = ticket.to_dict()
            mongo.insert_one(collection_name= 'tickets', data=data)
            producer.send_message('tickets', key=str(new_data["id"]), event= new_event)
            
class NerEventHandler(AbstractEventHandler):
    def handle_event(self, event: Event):
        data = event.payload
        mongo.update_one(collection_name= 'tickets', query= {'id': data['id']}, update_values= {'ner': data['value']})
        
class SumEventHandler(AbstractEventHandler):
    def handle_event(self, event: Event):
        data = event.payload
        mongo.update_one(collection_name= 'tickets', query= {'id': data['id']}, update_values= {'summary': data['value']})

class TagEventHandler(AbstractEventHandler):
    def handle_event(self, event: Event):
        data = event.payload
        mongo.update_one(collection_name= 'tickets', query= {'id': data['id']}, update_values= {'tags': data['value']})

class DeleteEventHandler(AbstractEventHandler):
    def handle_event(self, event: Event):
        deleted_data = event["before"]
        event = Event(
            source= 'ticket-command',
            op= 'u',
            payload= deleted_data
        )
        mongo.delete_one(collection_name= 'tickets', query= {'id': deleted_data['id']})
        
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
        else:
            print(f"[UNKNOWN] Event received: {event}")