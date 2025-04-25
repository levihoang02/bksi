from pymongo import MongoClient
from utils.config import Config

config = Config()

class MongoDBService:
    def __init__(self, URI, db_name='mydb'):
        self.URI = URI
        self.db_name = db_name
        self.client = self._connect()
        self.db = self.client[self.db_name]
    
    def _connect(self):
        """Establish MongoDB connection"""
        return MongoClient(self.URI)
    
    def get_collection(self, collection_name):
        """Get a MongoDB collection"""
        return self.db[collection_name]

    def insert_one(self, collection_name, data):
        """Insert a single document"""
        collection = self.get_collection(collection_name)
        return collection.insert_one(data).inserted_id

    def insert_many(self, collection_name, data_list):
        """Insert multiple documents"""
        collection = self.get_collection(collection_name)
        return collection.insert_many(data_list).inserted_ids

    def find_one(self, collection_name, query):
        """Find a single document"""
        collection = self.get_collection(collection_name)
        return collection.find_one(query)

    def find_many(self, collection_name, query):
        """Find multiple documents."""
        collection = self.get_collection(collection_name)
        return list(collection.find(query))

    def update_one(self, collection_name, query, update_values):
        """Update a single document."""
        collection = self.get_collection(collection_name)
        return collection.update_one(query, {"$set": update_values})

    def delete_one(self, collection_name, query):
        """Delete a single document."""
        collection = self.get_collection(collection_name)
        return collection.delete_one(query)

    def delete_many(self, collection_name, query):
        """Delete multiple documents."""
        collection = self.get_collection(collection_name)
        return collection.delete_many(query)

    def close_connection(self):
        """Close the MongoDB connection."""
        self.client.close()
        
mongo = MongoDBService(config.MONGO_URI, db_name= config.MONGODB_DATABASE)