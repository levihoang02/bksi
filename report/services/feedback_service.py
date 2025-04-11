from pymongo import MongoClient
from datetime import datetime, timedelta
from models.feedback import Feedback

class FeedbackService:
    def __init__(self, mongo_uri):
        self.client = MongoClient(mongo_uri)
        self.db = self.client.feedback_db
        self.collection = self.db.feedbacks

    def save_feedback(self, feedback: Feedback):
        return self.collection.insert_one(feedback.to_dict())

    def get_metrics(self, service_name, days=7):
        start_date = datetime.utcnow() - timedelta(days=days)
        
        pipeline = [
            {
                '$match': {
                    'service_name': service_name,
                    'timestamp': {'$gte': start_date}
                }
            },
            {
                '$group': {
                    '_id': '$feedback_type',
                    'total': {'$sum': 1},
                    'positive': {
                        '$sum': {'$cond': [{'$eq': ['$value', True]}, 1, 0]}
                    }
                }
            }
        ]
        
        results = list(self.collection.aggregate(pipeline))
        
        metrics = {
            'thumbs_up_rate': 0,
            'usage_rate': 0,
            'rejection_rate': 0,
            'total_feedback': 0
        }
        
        for result in results:
            if result['_id'] == 'thumbs':
                metrics['thumbs_up_rate'] = (result['positive'] / result['total']) * 100 if result['total'] > 0 else 0
            elif result['_id'] == 'usage':
                metrics['usage_rate'] = (result['positive'] / result['total']) * 100 if result['total'] > 0 else 0
            elif result['_id'] == 'rejection':
                metrics['rejection_rate'] = (result['positive'] / result['total']) * 100 if result['total'] > 0 else 0
            
            metrics['total_feedback'] += result['total']
            
        return metrics

    def get_suggestions(self, service_name, limit=10):
        return list(self.collection.find(
            {
                'service_name': service_name,
                'suggestion': {'$ne': None}
            },
            {'suggestion': 1, 'timestamp': 1, '_id': 0}
        ).sort('timestamp', -1).limit(limit))