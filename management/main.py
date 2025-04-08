from flask import Flask, request, jsonify
import os
from utils.docker import build_image_from_skeleton, create_and_run_container, remove_container_from_id
from models.database import Database
from dotenv import load_dotenv
import uuid
from models.service import Service
from models.serviceInstance import ServiceInstance

load_dotenv()

# APP VARIBALES
SKELETON_PROCESSOR_PATH = os.path.join("skeleton", "modules", "processor", "process.py")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DATABASE_URL = f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

app = Flask(__name__)


db = Database(DATABASE_URL)
db.create_all()
session = db.create_session()


@app.route("/service", methods=["POST"])
def create_container():
    containers = []
    try:
        name = request.form.get("name")
        host = request.form.get("host")
        ports = request.form.getlist("port")
        endPoint = request.form.get("endPoint")
        replicas = int(request.form.get("replicas")) if request.form.get("replicas") else 1
        image = name
        file = request.files.get("process_file")

        if not name or not file:
            return jsonify({"error": "Lack of name or file"}), 400

        if not file.filename.endswith(".py"):
            return jsonify({"error": "You must insert process.py file"}), 400

        with session.begin():
            service = session.query(Service).filter_by(Sname=name).first()
            if not service:
                service = Service(Sname= name)
                session.add(service)
                session.flush()
                
                # Overwrite process.py
                file.save(SKELETON_PROCESSOR_PATH)

                # Build image and run container
                build_image_from_skeleton(image)
            
            for i in range(replicas):
                container_uuid = str(uuid.uuid4())
                container_name = f"{name}_{container_uuid}"
                container_port = ports[i]
                new_instance = ServiceInstance(host= host, port= container_port, endPoint= endPoint, 
                                         status= True, service_id= service.id, container_id= None)
            
                container = create_and_run_container(image, container_name, container_port)
                new_instance.container_id = container.id
                session.add(new_instance)
                containers.append(container)
        
        data = []
        for c in containers:
            data.append({"container_id": c.id, "container_name": c.name})
            
        return jsonify({
            "status": "success",
            "result": data
        })

    except Exception as e:
        session.rollback()
        for c in containers:
            c.stop()
            c.remove(force=True)
        return jsonify({"error": str(e)}), 500
    
@app.route("/service", methods=["DELETE"])
def remove_service():
    try:
        id = request.form.get("id")
        with session.begin():
            service_instaces = session.query(ServiceInstance).filter_by(service_id= id).all()
            session.query(ServiceInstance).filter_by(service_id= id).delete(synchronize_session='fetch')
            session.flush()
            session.query(Service).filter_by(id= id).delete(synchronize_session='fetch')
            
            for instance in service_instaces:
                remove_container_from_id(instance.container_id)
        
        return jsonify({
            "status": "success"
        })
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3200)