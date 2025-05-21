from flask import Blueprint, jsonify, request
from services.feedback_service import FeedbackService
from models.feedback import Feedback
from utils.config import Config

feedback_bp = Blueprint('feedback', __name__)
feedback_service = FeedbackService(Config.MONGO_URI, Config.MONGO_DB_NAME, Config.MONGO_COLLECTION_NAME)

@feedback_bp.route('/feedback', methods=['POST'])
def submit_feedback():
    try:
        data = request.json
        for d in data:
            feedback = Feedback(
                service_name=d['service_name'],
                feedback_type=d['feedback_type'],
                value=d['value'],
            )
            feedback_service.save_feedback(feedback)
        return jsonify({'message': 'Feedback received successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@feedback_bp.route('/metrics/<service_name>', methods=['GET'])
def get_metrics(service_name):
    try:
        metrics = feedback_service.get_metrics(service_name)
        return jsonify(metrics)
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
@feedback_bp.route('/feedbacks', methods=['GET'])
def get_all_service_metrics():
    try:
        days = request.args.get('days', default=None, type=int)
        metrics = feedback_service.get_all_metrics(days=days)
        return jsonify(metrics)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@feedback_bp.route('/suggestions/<service_name>', methods=['GET'])
def get_suggestions(service_name):
    try:
        suggestions = feedback_service.get_suggestions(service_name)
        return jsonify(suggestions)
    except Exception as e:
        return jsonify({'error': str(e)}), 400