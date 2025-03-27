from fastapi import FastAPI, Request, HTTPException
from database.mongo import MongoDBService
from utils.config import Config
from models.ticket import Ticket
from kafka.producer import ProducerService
import json

config = Config()

database_service = MongoDBService(config.MONGODB_HOST, config.MONGODB_PORT, config.MONGODB_DATABASE, 
                                  config.DB_USERNAME, config.DB_PASSWORD)

kafka_config = {'bootstrap.servers': config.KAFKA_BROKERS_EXTERNAL,
                'compression.type': 'lz4'}

app = FastAPI()

@app.post("/ticket")
async def create_new_ticket(request: Request):
    try:
        body = await request.json()
        payload = body.get("payload", {})

        # Trích xuất dữ liệu từ payload
        id = payload.get("id")
        content = payload.get("content", "")
        entities1 = payload.get("entities1", [])
        entities2 = payload.get("entities2", [])
        summarize = payload.get("summarize", "")
        intents = payload.get("intents", [])

        new_ticket = Ticket(id=id, content=content, entities1=entities1, entities2=entities2, summarize=summarize, intents=intents)

        database_service.insert_one("tickets", new_ticket.dict())
        producer = ProducerService(kafka_config)
        message = json.dumps({'id': id, 'content': content}, ensure_ascii=False).encode('utf-8')
        producer.send_message('ticket',
                        key=str(id).encode('utf-8'),  # Convert id to string and then to bytes
                        message=message
        )

        return {"message": "Ticket created successfully", "ticket": new_ticket.dict()}
    
    except Exception as e:
        return {"error": str(e)}
    
@app.put("/ticket/{ticket_id}")
async def update_ticket(ticket_id: str, request: Request):
    try:
        update_data = await request.json()

        if not update_data:
            raise HTTPException(status_code=400, detail="No update data provided")

        update_fields = {f"set__{key}": value for key, value in update_data.items()}

        updated_count = database_service.update_one("tickets", {"id": ticket_id}, update_fields)

        if updated_count == 0:
            raise HTTPException(status_code=404, detail=f"Ticket with id {ticket_id} not found")

        return {"message": "Ticket updated successfully", "updated_fields": update_data}

    except Exception as e:
        return {"error": str(e)}

