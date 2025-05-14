from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from datetime import datetime, timedelta
from models.metric import Metric
import json

class MetricService:
    def __init__(self, mongo_uri, db_name, collection_name):
        self.client = MongoClient(mongo_uri)
        self.db_name = db_name
        self.db = self.client[self.db_name]
        self.collection_name = collection_name
        self.collection = self.db[self.collection_name]
        self.collection.create_index("metric_name", unique=True)

    def save_metric(self, metric: Metric):
        try:
            return self.collection.insert_one(metric.to_dict())
        except DuplicateKeyError:
            print(f"[INFO] Metric '{metric.metric_name}' already exists. Skipping.")
            return None

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
            {"_id": 0, "metric_name": 1, "chart_type": 1, "prom_type": 1}  # Adjusted fields
        )
        result = list(cursor)
        return result

from utils.config import Config
config = Config()
# print(config.MONGO_URI)
metric_service = MetricService(config.MONGO_URI, 'metric_db', 'metrics')

def seed_metrics_from_json(file_path: str):
    try:
        with open(file_path, 'r') as f:
            metrics_data = json.load(f)

        existing_metrics_cursor = metric_service.collection.find(
            {}, {"_id": 0, "metric_name": 1}
        )
        existing_metric_names = {m["metric_name"] for m in existing_metrics_cursor}

        new_metrics = [
            item for item in metrics_data
            if item["metric_name"] not in existing_metric_names
        ]

        for item in new_metrics:
            metric = Metric(metric_name=item["metric_name"], chart_type=item["chart_type"], prom_type=item["prom_type"])
            metric_service.save_metric(metric)

        print("Inserted new metrics to MongoDB.")

    except Exception as e:
        print(f"Failed to seed metrics: {e}")
        