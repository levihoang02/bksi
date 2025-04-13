from flask import Blueprint, jsonify, request
from services.feedback_service import FeedbackService
from models.feedback import Feedback
from utils.config import Config

feedback_bp = Blueprint('feedback', __name__)
feedback_service = FeedbackService(Config.MONGO_URI)

@feedback_bp.route('/feedback', methods=['POST'])
def submit_feedback():
    try:
        data = request.json
        feedback = Feedback(
            service_name=data['service_name'],
            feedback_type=data['feedback_type'],
            value=data['value'],
            suggestion=data.get('suggestion')
        )
        feedback_service.save_feedback(feedback)
        return jsonify({'message': 'Feedback received successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@feedback_bp.route('/metrics/<service_name>', methods=['GET'])
def get_metrics(service_name):
    try:
        days = request.args.get('days', default=7, type=int)
        metrics = feedback_service.get_metrics(service_name, days)
        return jsonify(metrics)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@feedback_bp.route('/suggestions/<service_name>', methods=['GET'])
def get_suggestions(service_name):
    try:
        limit = request.args.get('limit', default=10, type=int)
        suggestions = feedback_service.get_suggestions(service_name, limit)
        return jsonify(suggestions)
    except Exception as e:
        return jsonify({'error': str(e)}), 400