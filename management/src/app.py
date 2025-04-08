from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import docker
import jwt
import json
import yaml
import os
from datetime import datetime
from jsonschema import validate
from typing import Dict, Optional
import logging
import secrets

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Secure Container Management API")
security = HTTPBearer()

# Load configuration from secrets
JWT_SECRET = open('/run/secrets/jwt_secret').read().strip()
ALLOWED_USERS = json.loads(os.getenv("ALLOWED_USERS", '["admin"]'))
MAX_CONTAINERS_PER_USER = int(os.getenv("MAX_CONTAINERS_PER_USER", "5"))

# Initialize Docker client with Swarm mode
docker_client = docker.from_env()
docker_client.swarm.reload()  # Ensure we're in swarm mode

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> Dict:
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        if payload["username"] not in ALLOWED_USERS:
            raise HTTPException(status_code=403, detail="User not authorized")
        return payload
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(status_code=500, detail="Authentication error")

def load_and_validate_schema():
    schema_path = "/app/modules/validation/schema.json"
    try:
        with open(schema_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load schema: {str(e)}")
        raise HTTPException(status_code=500, detail="Schema loading error")

def validate_module_config(config: Dict):
    schema = load_and_validate_schema()
    try:
        validate(instance=config, schema=schema)
    except Exception as e:
        logger.error(f"Configuration validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid configuration: {str(e)}")

def check_resource_limits(config: Dict):
    # Check CPU and memory limits
    cpu_limit = float(config["resources"]["cpu"])
    memory_limit = config["resources"]["memory"].rstrip("MG")
    
    if cpu_limit > 1.0 or int(memory_limit) > 1024:
        raise HTTPException(status_code=400, detail="Resource limits exceeded")

def get_user_services(username: str) -> int:
    try:
        services = docker_client.services.list(
            filters={"label": f"created_by={username}"}
        )
        return len(services)
    except Exception as e:
        logger.error(f"Error checking user services: {str(e)}")
        raise HTTPException(status_code=500, detail="Service check error")

@app.post("/modules/create")
async def create_module(
    config: Dict,
    user: Dict = Depends(verify_token)
):
    try:
        # Validate configuration
        validate_module_config(config)
        check_resource_limits(config)

        # Check user service limit
        if get_user_services(user["username"]) >= MAX_CONTAINERS_PER_USER:
            raise HTTPException(status_code=400, detail="Maximum service limit reached")

        # Generate unique service name
        service_name = f"{config['name']}-{secrets.token_hex(4)}"

        # Create service with secure defaults
        service = docker_client.services.create(
            image=config["image"],
            name=service_name,
            replicas=1,
            networks=["app-network"],
            endpoint_spec=docker.types.EndpointSpec(
                ports={config.get("port", 80): 80}
            ),
            labels={
                "created_by": user["username"],
                "created_at": datetime.utcnow().isoformat(),
                "managed_by": "management-module"
            },
            deploy=docker.types.ServiceMode(
                replicas=1,
                restart_policy=docker.types.RestartPolicy(
                    condition="on-failure",
                    max_attempts=3
                ),
                resources=docker.types.Resources(
                    limits={
                        "cpus": config["resources"]["cpu"],
                        "memory": config["resources"]["memory"]
                    },
                    reservations={
                        "cpus": str(float(config["resources"]["cpu"]) * 0.5),
                        "memory": str(int(config["resources"]["memory"].rstrip("MG")) * 0.5) + "M"
                    }
                ),
                update_config=docker.types.UpdateConfig(
                    parallelism=1,
                    delay=10,
                    order="start-first"
                ),
                rollback_config=docker.types.RollbackConfig(
                    parallelism=1,
                    delay=10,
                    order="stop-first"
                )
            ),
            constraints=[
                "node.role == worker"
            ],
            cap_drop=["ALL"],
            security_opt=["no-new-privileges:true"],
            read_only=True,
            tmpfs=["/tmp", "/var/run"]
        )

        logger.info(f"Service {service_name} created by {user['username']}")
        return {"status": "success", "service_id": service.id}

    except docker.errors.APIError as e:
        logger.error(f"Docker API error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Service creation failed: {str(e)}")
    except Exception as e:
        logger.error(f"Error creating service: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/modules/{service_id}")
async def delete_module(
    service_id: str,
    user: Dict = Depends(verify_token)
):
    try:
        service = docker_client.services.get(service_id)
        
        # Verify ownership
        if service.attrs["Spec"]["Labels"].get("created_by") != user["username"]:
            raise HTTPException(status_code=403, detail="Not authorized to delete this service")

        service.remove()
        logger.info(f"Service {service_id} deleted by {user['username']}")
        return {"status": "success"}

    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail="Service not found")
    except Exception as e:
        logger.error(f"Error deleting service: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/modules/list")
async def list_modules(
    user: Dict = Depends(verify_token)
):
    try:
        services = docker_client.services.list(
            filters={"label": f"created_by={user['username']}"}
        )
        return {
            "services": [
                {
                    "id": s.id,
                    "name": s.name,
                    "replicas": s.attrs["ServiceStatus"]["RunningTasks"],
                    "created": s.attrs["CreatedAt"]
                }
                for s in services
            ]
        }
    except Exception as e:
        logger.error(f"Error listing services: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3200) 