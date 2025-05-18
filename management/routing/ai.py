from threading import Lock
from models.service  import Service
from sqlalchemy.orm import Session

_round_robin_index = {}
_rr_lock = Lock()

def route_round_robin(session: Session, service_name: str):
    service: Service = session.query(Service).filter_by(Sname=service_name).first()

    if not service or not service.service_instances:
        raise ValueError(f"No instances found for service: {service_name}")

    active_instances = [inst for inst in service.service_instances if inst.status]

    if not active_instances:
        raise ValueError(f"No active instances found for service: {service_name}")

    with _rr_lock:
        current_index = _round_robin_index.get(service_name, 0)
        instance = active_instances[current_index % len(active_instances)]
        _round_robin_index[service_name] = (current_index + 1) % len(active_instances)

    return instance