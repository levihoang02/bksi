from abc import ABC, abstractmethod
from kafka_utils.event import Event, EventType
from kafka_utils.producer import producer, send_to_dlq
from utils.config import Config
from helpers.html import decode_html
from database.mongo import mongo
from models.ticket import Ticket
from router.factory import ModelRouterFactory

config = Config()

tasks = [e.value.lower() for e in EventType]

class AbstractEventHandler(ABC):
    @abstractmethod
    def handle_event(self, event: Event):
        pass
    
class InsertEventHandler(AbstractEventHandler):
    def handle_event(self, event: Event):
        new_data = event.to_dict()
        payload = new_data.get("payload")
        mode = 'async'
        if(payload.get("created_by") == "customer"):
            raw_content = decode_html(payload.get("message"))
            ticket_id = payload.get("id")
            new_payload = {
                "ticket_id": payload.get("id"),
                "content":  raw_content
            }
            # new_event = Event(
            #         source='management', 
            #         op=EventType.CREATE,
            #         payload= new_payload
            #     )
            ticket = Ticket(id= payload.get("id"), content= raw_content)
            data = ticket.to_dict()
            mongo.insert_one(collection_name= 'tickets', data=data)
            for task in tasks:
                router = ModelRouterFactory.get_router(task)
                router.route(mode, EventType.CREATE, ticket_id, new_payload)
            
# class NerEventHandler(AbstractEventHandler):
#     def handle_event(self, event: Event):
#         data = event.to_dict()
#         payload = data.get("payload")
#         ticket_id = payload.get('ticket_id')
#         if ticket_id is None:
#             raise ValueError("Missing 'ticket_id' in event payload for NER update.")
#         mongo.update_one(collection_name= 'tickets', query= {'id': ticket_id}, update_values= {'ner': payload.get('value')})
        
# class SumEventHandler(AbstractEventHandler):
#     def handle_event(self, event: Event):
#         data = event.to_dict()
#         payload = data.get("payload")
#         ticket_id = payload.get('ticket_id')
#         print(payload.get('value'))
#         if ticket_id is None:
#             raise ValueError("Missing 'ticket_id' in event payload for NER update.")
#         mongo.update_one(collection_name= 'tickets', query= {'id': ticket_id}, update_values= {'summary': payload.get('value')})

# class TagEventHandler(AbstractEventHandler):
#     def handle_event(self, event: Event):
#         data = event.to_dict()
#         payload = data.get("payload")
#         mongo.update_one(collection_name= 'tickets', query= {'id': payload.get('ticket_id')}, update_values= {'tags': payload.get('value')})
        
class GenericAIEventHandler(AbstractEventHandler):
    def handle_event(self, event: Event):
        task = "ai-sample"
        mode = 'async'
        data = event.to_dict()
        payload = data.get("payload")
        ticket_id = payload.get('ticket_id')
       
        if not payload or not id:
            raise ValueError("Missing payload or ticket_id in payload")

        router = ModelRouterFactory.get_router(task)
        result = router.route(mode, EventType.CREATE, ticket_id, payload)
        if mode == "async":
            mongo.update_one(collection_name= 'tickets', query= {'id': ticket_id}, update_values= {task: payload.get('value')})
        return

class DeleteEventHandler(AbstractEventHandler):
    def handle_event(self, event: Event):
        data = event.to_dict()
        payload = data.get("payload")
        mongo.delete_one(collection_name= 'tickets', query= {'id': int(payload.get('id'))})
        
class EventProcessor:
    def __init__(self):
        self.handlers = {
            EventType.CREATE: InsertEventHandler,
            EventType.NER: GenericAIEventHandler,
            EventType.DELETE: DeleteEventHandler,
            EventType.SUMMARIZE: GenericAIEventHandler,
            EventType.TAG: GenericAIEventHandler,
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