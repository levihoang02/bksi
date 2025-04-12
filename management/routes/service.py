from flask import request, jsonify, send_file, Blueprint
import os, uuid, shutil
from models.service import Service
from models.serviceInstance import ServiceInstance
from models.database import SKELETON_PROCESSOR_PATH, ENV_PATH, db
from utils.file import analyze_process_file, has_process_function
from kafka_utils.producer import producer
from kafka_utils.event import Event, EventType

service_bp = Blueprint("service", __name__)

def get_zip_file_path(name):
    zip_file_path = os.path.join("containers", f"{name}_skeleton.zip")
    return zip_file_path

@service_bp.route("/service", methods=["POST"])
def create_container():
    session = db.create_session()
    try:
        name = request.form.get("name")
        host = request.form.get("host")
        ports = request.form.getlist("port")
        endPoint = request.form.get("endPoint")
        replicas = int(request.form.get("replicas")) if request.form.get("replicas") else 1

        with session.begin():
            service = session.query(Service).filter_by(Sname=name).first()
            if not service:
                service = Service(Sname= name)
                session.add(service)
                session.flush()
            
            for i in range(replicas):
                new_instance = ServiceInstance(host= host, port= ports[i], endPoint= endPoint, 
                                status= True, service_id= service.id, skeleton_path= None)
                session.add(new_instance)
                session.flush()
                new_event = Event(
                    source='management', 
                    op=EventType.CREATE,
                    payload={
                        'host': host,
                        'port': ports[i],
                        'id': new_instance.id,
                        'job': name
                    }
                )
                producer.send_event(topic='dashboard', event = new_event)
        
            return jsonify({
                "status": "success"
            })
    except Exception as e:
        session.rollback()
        session.close()
        return jsonify({"error": str(e)}), 500
    
@service_bp.route("/service", methods=["DELETE"])
def remove_service():
    session = db.create_session()
    try:
        id = request.form.get("id")
        with session.begin():
            service = session.query(Service).filter_by(id= id).first()
            instances = session.query(ServiceInstance).filter_by(service_id= id).all()
            session.query(ServiceInstance).filter_by(service_id= id).delete(synchronize_session='fetch')
            session.flush()
            service = session.query(Service).filter_by(id= id).first()
            session.query(Service).filter_by(id= id).delete(synchronize_session='fetch')
            for instance in instances:
                new_event = Event(
                    source='management', 
                    op=EventType.DELETE,
                    payload={
                        'id': instance.id,
                        'host': instance.host,
                        'port': instance.port,
                        'name': service.Sname
                    }
                )
                producer.send_event(topic='dashboard', event = new_event)
        return jsonify({
            "status": "success"
        })
    except Exception as e:
        session.rollback()
        session.close()
        return jsonify({"error": str(e)}), 500
    
@service_bp.route("/download", methods=["GET"])
def download_skeleton_file():
    session = db.create_session()
    try:
        id = request.form.get("id")
        service = session.query(Service).filter_by(id= id).first()
        zip_file_path = get_zip_file_path(service.Sname)
        if not os.path.exists(zip_file_path):
            return {"error": "File not found"}, 404
        
        return send_file(
            zip_file_path,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f"{service.Sname}.zip"
        )
    except Exception as e:
        session.rollback()
        session.close()
        return jsonify({"error": str(e)}), 500
    
@service_bp.route("/instance", methods=["POST"])
def create_new_instance():
    session = db.create_session()
    try:
        id = request.form.get("id")
        host = request.form.get("host")
        port = request.form.getlist("port")
        endPoint = request.form.get("endPoint")
        zip_file_path= ""
        with session.begin():
            service = session.query(Service).filter_by(id= id).first()
            
            new_instance = ServiceInstance(host= host, port= port, endPoint= endPoint, 
                            status= True, service_id= service.id, skeleton_path= zip_file_path)
            session.add(new_instance)
            new_event = Event(
                    source='management', 
                    op=EventType.CREATE,
                    payload={
                        'host': host,
                        'port': port,
                        'id': new_instance.id,
                        'name': service.Sname
                    }
                )
            producer.send_event(topic='dashboard', event = new_event)
        
        return jsonify({
            "status": "success"
        })
    except Exception as e:
        session.rollback()
        session.close()
        return jsonify({"error": str(e)}), 500

@service_bp.route("/instance", methods=["DELETE"])
def remove_instance():
    session = db.create_session()
    try:
        id = request.form.get("id")
        with session.begin():
            instance= session.query(ServiceInstance).filter_by(id= id).first()
            service= session.query(ServiceInstance).filter_by(id= instance.service_id).first()
            session.query(ServiceInstance).filter_by(id= id).delete(synchronize_session='fetch')
            
            new_event = Event(
                    source='management', 
                    op=EventType.DELETE,
                    payload={
                        'id': instance.id,
                        'host': instance.host,
                        'port': instance.port,
                        'name': service.Sname
                    }
                )
            producer.send_event(topic='dashboard', event = new_event)
        return jsonify({
                "status": "success"
            })
    except Exception as e:
        session.close()
        return jsonify({"error": str(e)}), 500

