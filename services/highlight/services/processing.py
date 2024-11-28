import os
import json

def process_data(data):
    file_path = os.path.join(os.path.dirname(__file__), "../utils/test.json")
    file_path = os.path.abspath(file_path)

    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        
    return data[0]["entities"]
