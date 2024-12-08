from flask import Flask, jsonify, request
from utils.config import Config
import time
from services.processing import process_data


app = Flask(__name__)
config = Config()


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "highlight-service",
        "timestamp": time.time()
        })
    
@app.route('/use', methods=['POST'])
def use_ner():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        result, status_code = process_data(data)
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)