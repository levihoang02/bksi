from datetime import datetime

class Feedback:
    def __init__(self, service_name, feedback_type, value, suggestion=None):
        self.service_name = service_name
        self.feedback_type = feedback_type  # thumbs/usage/rejection
        self.value = value  # True/False for thumbs, float for rates
        self.suggestion = suggestion
        self.timestamp = datetime.utcnow()
    
    def to_dict(self):
        return {
            'service_name': self.service_name,
            'feedback_type': self.feedback_type,
            'value': self.value,
            'suggestion': self.suggestion,
            'timestamp': self.timestamp
        }