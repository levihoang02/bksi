from flask import jsonify, jsonify, Blueprint
from kafka_utils.event import Event, EventType
from database.mongo import mongo

ticket_bp = Blueprint("ticket", __name__)

@ticket_bp.route("/use/<ticket_id>", methods=["GET"])
def get_ticket_by_id(ticket_id):
    try:
        id = int(ticket_id)
        # Find ticket by 'id'
        ticket = mongo.find_one('tickets', {'id': id})
        
        if ticket:
            return jsonify(ticket), 200
        else:
            return jsonify({"error": "Ticket not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    