from services.database import get_session
from sqlalchemy.orm import sessionmaker, joinedload, relationship
from sqlalchemy import Column, String, ForeignKey, DateTime, Boolean, CHAR, BigInteger
import uuid

from services.database import engine, Base, get_session

class Service(Base):
    __tablename__ = 'services'
    
    id = Column(CHAR(36, 'utf8mb4_bin'), primary_key=True, default=lambda: str(uuid.uuid4()))
    Sname = Column(String(255), unique=True, nullable=False)  # Ensure nullable=False
    
    instances = relationship("ServiceInstance", back_populates="service")

    def __repr__(self):
        return f"<Service(name={self.Sname}, status={self.status})>"
    
class ServiceInstance(Base):
    __tablename__ = 'serviceInstances'
    
    id = Column(CHAR(36, 'utf8mb4_bin'), primary_key=True, default=lambda: str(uuid.uuid4()))
    host = Column(String(255), nullable=True)
    port = Column(String(255), nullable=True)
    endPoint = Column(String(255), nullable=True)
    status = Column(Boolean, nullable=False, default=True)
    ServiceId = Column(CHAR(36, 'utf8mb4_bin'), ForeignKey('services.id'), nullable=False)
    
    service = relationship("Service", back_populates="instances")

    def __repr__(self):
        return f"<Service(name={self.Sname}, status={self.status})>"

def get_services():
    """Fetch all services from database"""
    session = get_session()
    services = session.query(Service).all()
    result = [
        {
            "id": service.id,
            "name": service.Sname
        }
        for service in services
    ]
    session.close()
    return result

def get_instance(service_id):
    """Fetch all instances for a specific service ID"""
    session = get_session()
    instances = session.query(ServiceInstance).filter(ServiceInstance.service_id == service_id).all()
    result = [
        {
            "id": instance.id,
            "host": instance.host,
            "port": instance.port,
            "endPoint": instance.endPoint,
            "status": instance.status
        }
        for instance in instances
    ]
    session.close()
    return result

Base.metadata.create_all(engine)