from flask import jsonify, jsonify, Blueprint
from kafka_utils.event import Event, EventType
from database.mongo import mongo
from models.ticket import Ticket

ticket_bp = Blueprint("ticket", __name__)

@ticket_bp.route("/use/<ticket_id>", methods=["GET"])
def get_ticket_by_id(ticket_id):
    try:
        id = int(ticket_id)
        # Find ticket by 'id'
        ticket = mongo.find_one('tickets', {'id': id})
        
        if ticket:
            if '_id' in ticket:
                ticket['_id'] = str(ticket['_id'])

            return jsonify(ticket), 200
        else:
            new_ticket = Ticket(id=id, content=None, tags=[], summary=None, ner=[])
            mongo.insert_one('tickets', new_ticket.to_dict())
            return jsonify({
                "message": "Ticket not found, new ticket created.",
                "ticket_id": ticket_id
            }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    