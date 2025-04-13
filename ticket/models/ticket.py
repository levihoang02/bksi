from datetime import datetime

class Ticket:
    def __init__(self, id, content, tags= [], summary=None, ner=[]):
        self.id = id
        self.content = content
        self.tags = tags
        self.summary = summary,
        self.ner = ner
        self.timestamp = datetime.utcnow()
    
    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'tags': self.tags,
            'ner': self.ner,
            'summary': self.summary,
            'timestamp': self.timestamp
        }