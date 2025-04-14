from pymongo import MongoClient
from datetime import datetime, timedelta
from models.feedback import Feedback

class FeedbackService:
    def __init__(self, mongo_uri, db_name, collection_name):
        self.client = MongoClient(mongo_uri)
        self.db_name = db_name
        self.db = self.client[self.db_name]
        self.collection_name = collection_name
        self.collection = self.db[self.collection_name]

    def save_feedback(self, feedback: Feedback):
        return self.collection.insert_one(feedback.to_dict())

    def get_metrics(self, service_name, days=None):
        if days is not None:
            start_date = datetime.utcnow() - timedelta(days=days)
        else:
            start_date = datetime(1970, 1, 1)
        
        pipeline = [
            {
                '$match': {
                    'service_name': service_name,
                    'timestamp': {'$gte': start_date},
                    'feedback_type': {'$ne': 'suggestion'} 
                }
            },
            {
                '$group': {
                    '_id': '$feedback_type',
                    'total': {'$sum': 1},
                    'positive': {
                        '$sum': {'$cond': [{'$eq': ['$value', 1]}, 1, 0]}
                    },
                    'neutral': {
                        '$sum': {'$cond': [{'$eq': ['$value', 0]}, 1, 0]}
                    },
                    'negative': {
                        '$sum': {'$cond': [{'$eq': ['$value', -1]}, 1, 0]}
                    }
                }
            }
        ]
        
        results = list(self.collection.aggregate(pipeline))
        
        metrics = {
            'thumbs_up_total': 0,
            'neutral_total': 0,
            'thumbs_down_total': 0,
            'usage_total': 0,
            'rejection_total': 0,
            'total_feedback': 0
        }
        
        for result in results:
            if result['_id'] == 'rate':
                metrics['thumbs_up_total'] = result['positive']
                metrics['neutral_total'] = result['neutral']
                metrics['thumbs_down_total'] =  result['negative']
            elif result['_id'] == 'usage':
                metrics['usage_total'] = result['positive']
                metrics['rejection_total'] = result['negative']
            
            metrics['total_feedback'] += result['total']
            
        return metrics

    def get_suggestions(self, service_name, limit=None):
        query = {
            'service_name': service_name,
            'feedback_type': {'$eq': 'suggestion'},
        }
        if limit is not None:
             return list(self.collection.find(query, {'value': 1, 'timestamp': 1, '_id': 0})
                    .sort('timestamp', -1)
                    .limit(limit))
        else:
            return list(self.collection.find(query, {'value': 1, 'timestamp': 1, '_id': 0})
                    .sort('timestamp', -1))