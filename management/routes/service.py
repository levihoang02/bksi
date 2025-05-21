from flask import request, jsonify, send_file, Blueprint
import os, uuid, shutil
from models.service import Service
from models.serviceInstance import ServiceInstance
from models.database import SKELETON_PROCESSOR_PATH, ENV_PATH, db
from kafka_utils.producer import producer
from kafka_utils.event import Event, EventType
from routing.ai import route_round_robin

service_bp = Blueprint("service", __name__)

def get_zip_file_path(name):
    zip_file_path = os.path.join("containers", f"{name}_skeleton.zip")
    return zip_file_path

@service_bp.route("/service", methods=["POST"])
def create_new_service():
    session = db.create_session()
    try:
        data = request.json
        name = data.get("name")
        hosts = data.get("hosts", [])
        ports = data.get("ports", [])  # Assuming ports can be a list
        endPoint = data.get("endPoint")
        replicas = int(data.get("replicas", 1))
        metrics = data.get("metrics")

        with session.begin():
            service = session.query(Service).filter_by(Sname=name).first()
            if not service:
                service = Service(Sname= name)
                session.add(service)
                session.flush()
            
            for i in range(replicas):
                new_instance = ServiceInstance(host= hosts[i], port= ports[i], endPoint= endPoint, 
                                status= True, service_id= service.id, skeleton_path= None)
                session.add(new_instance)
                session.flush()
                new_event = Event(
                    source='management', 
                    op=EventType.CREATE,
                    payload={
                        'host': hosts[i],
                        'port': ports[i],
                        'id': new_instance.id,
                        'job': name,
                        'metrics': metrics
                    }
                )
                producer.send_event(topic='dashboard', event = new_event)
                producer.send_event(topic='models', event = new_event)
        
            return jsonify({
                "status": "success"
            })
    except Exception as e:
        session.rollback()
        session.close()
        return jsonify({"error": str(e)}), 500
    
@service_bp.route("/services", methods=["GET"])
def get_all_services():
    session = db.create_session()
    try:
        services = session.query(Service).all()
        result = []
        for service in services:
            instances = session.query(ServiceInstance).filter_by(service_id=service.id).all()
            result.append({
                "name": service.Sname,
                "id": service.id,
                "instances": [
                    {
                        "id": instance.id,
                        "host": instance.host,
                        "port": instance.port,
                        "endPoint": instance.endPoint,
                    }
                    for instance in instances
                ]
            })
        return jsonify(result)
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()
    
@service_bp.route("/service/<name>", methods=["DELETE"])
def remove_service(name):
    session = db.create_session()
    try:
        with session.begin():
            service = session.query(Service).filter_by(Sname= name).first()
            instances = session.query(ServiceInstance).filter_by(service_id= service.id).all()
            session.query(ServiceInstance).filter_by(service_id= service.id).delete(synchronize_session='fetch')
            session.flush()
            
            session.query(Service).filter_by(Sname= name).delete(synchronize_session='fetch')
            for instance in instances:
                new_event = Event(
                    source='management', 
                    op=EventType.DELETE,
                    payload={
                        'id': instance.id,
                        'host': instance.host,
                        'port': instance.port,
                        'name': service.Sname,
                        'job': service.Sname,
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
    
@service_bp.route("/instance", methods=["POST"])
def create_new_instance():
    session = db.create_session()
    try:
        data = request.json
        id = data.get("id")
        host = data.get("host")
        port = data.get("port", [])
        endPoint = data.get("endPoint")
        zip_file_path= ""
        metrics = [
            "ai_request_total",
            "ai_request_latency_seconds",
            "model_inferences_total",
            "model_inference_errors_total",
            "model_response_time_seconds",
            "model_batch_size",
            "model_input_data_size_bytes",
            "model_output_data_size_bytes",
            "model_input_tokens_total",
            "model_output_tokens_total",
            "ai_model_accuracy",
            "ai_model_loss",
            "ai_memory_usage_bytes",
            "ai_cpu_usage_percent",
            "ai_gpu_memory_usage_bytes",
            "ai_gpu_utilization_percent"
        ]
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
                        'name': service.Sname,
                        'job': service.Sname,
                        'metrics': metrics
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

@service_bp.route("/instance/<id>", methods=["DELETE"])
def remove_instance(id):
    session = db.create_session()
    try:
        with session.begin():
            instance= session.query(ServiceInstance).filter_by(id= id).first()
            if not instance:
                return {"error": "Instance not found"}, 404
            service= session.query(Service).filter_by(id= instance.service_id).first()
            if not service:
                return {"error": "Service not found"}, 404
            session.query(ServiceInstance).filter_by(id= id).delete(synchronize_session='fetch')
            
            new_event = Event(
                    source='management', 
                    op=EventType.DELETE,
                    payload={
                        'id': instance.id,
                        'host': instance.host,
                        'port': instance.port,
                        'name': service.Sname,
                        'job': service.Sname,
                    }
                )
            producer.send_event(topic='dashboard', event = new_event)
        return jsonify({
                "status": "success"
            })
    except Exception as e:
        session.close()
        return jsonify({"error": str(e)}), 500
    
@service_bp.route("/route/<name>", methods=["POST"])
def routing(name):
    session = db.create_session()
    try:
        with session.begin():
            instance = route_round_robin(session, service_name=name)
            service = session.query(Service).filter_by(id=instance.service_id).first()

        return jsonify({
            "id": instance.id,
            "service_name": service.Sname if service else None,
            "status": "success",
            "host": instance.host,
            "port": instance.port,
            "endpoint": instance.endPoint,
            "url": f"http://{instance.host}:{instance.port}/{instance.endPoint.lstrip('/')}"
        })
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

