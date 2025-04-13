from pymongo import MongoClient
from datetime import datetime, timedelta
from models.metric import Metric

class MetricService:
    def __init__(self, mongo_uri, db_name, collection_name):
        self.client = MongoClient(mongo_uri)
        self.db_name = db_name
        self.db = self.client[self.db_name]
        self.collection_name = collection_name
        self.collection = self.db[self.collection_name]

    def save_metric(self, metric: Metric):
        return self.collection.insert_one(metric.to_dict())

    def get_metric(self, metric_name: str):
        metric = self.collection.find({'metric_name': metric_name})
        return metric
    
    def delete_metric(self, metric_name: str):
        result = self.collection.delete_one({"metric_name": metric_name})
        if result.deleted_count > 0:
            return {"message": "Metric deleted successfully."}
        else:
            return {"error": "Metric not found."}
    
    def get_metric_types(self, metric_names: list[str]) -> list[dict]:
        cursor = self.collection.find(
            {"metric_name": {"$in": metric_names}},
            {"_id": 0, "metric_name": 1, "chart_type": 1}  # Adjusted fields
        )
        result = list(cursor)
        return result

from utils.config import Config
config = Config()
metric_service = MetricService(config.MONGO_URI, 'metric_db', 'metrics')