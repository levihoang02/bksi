from datetime import datetime

class Feedback:
    def __init__(self, service_name, feedback_type, value):
        self.service_name = service_name
        self.feedback_type = feedback_type  # rate/usage/suggestion
        self.value = value  # -1, 0, 1 for rate, 1, -1 for usage/rejection and [] for suggestion
        self.timestamp = datetime.utcnow()
    
    def to_dict(self):
        return {
            'service_name': self.service_name,
            'feedback_type': self.feedback_type,
            'value': self.value,
            'timestamp': self.timestamp
        }