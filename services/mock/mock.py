from flask import Flask, request, jsonify
from marshmallow import Schema, fields
import json
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Load mock data
def load_mock_data():
    try:
        with open('test.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"error": "Mock data file not found"}

# Input validation schema
class NERRequestSchema(Schema):
    payload = fields.Str(required=True)
    id = fields.Int(required=True)

# Routes
@app.route('/ner', methods=['POST'])
def ner():
    # Validate input
    schema = NERRequestSchema()
    print(request.json)
    errors = schema.validate(request.json)
    if errors:
        return jsonify({"error": "Invalid input", "details": errors}), 400

    request_id = request.json.get('id')
    
    # Get mock data
    mock_data = load_mock_data()
    
    # Check if id is valid
    if not isinstance(mock_data, list) or request_id >= len(mock_data):
        return jsonify({"error": f"No data found for id {request_id}"}), 404
        
    # Return specific mock response based on id
    return jsonify(mock_data[request_id])

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8100))
    app.run(host='0.0.0.0', port=port, debug=True)
