from flask import request, jsonify, send_file, Blueprint
from kafka_utils.event import Event, EventType
from database.mongo import mongo

ticket_bp = Blueprint("ticket", __name__)

@ticket_bp.route("/<ticket_id>", methods=["GET"])
def get_ticket_by_id(ticket_id):
    try:
       ticket = mongo.find_one('tickets', {'id': ticket_id})
       return ticket if ticket else "Ticket not found", 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    