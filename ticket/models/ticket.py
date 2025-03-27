from pydantic import BaseModel

class Ticket(BaseModel):
    id: int
    content: str
    entities1: list
    entities2: list
    summarize: str
    intents: list