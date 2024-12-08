from services.database import get_session
from sqlalchemy.orm import sessionmaker, joinedload, relationship
from sqlalchemy import Column, String, ForeignKey, DateTime, Boolean, CHAR, BigInteger
import uuid

from services.database import engine, Base, get_session

class Service(Base):
    __tablename__ = 'services'
    
    id = Column(CHAR(36, 'utf8mb4_bin'), primary_key=True, default=lambda: str(uuid.uuid4()))
    Sname = Column(String(255), unique=True, nullable=False)  # Ensure nullable=False
    host = Column(String(255), nullable=True)
    port = Column(String(255), nullable=True)
    endPoint = Column(String(255), nullable=True)
    status = Column(Boolean, nullable=False, default=True)  # Ensure nullable=False and default=True

    def __repr__(self):
        return f"<Service(name={self.Sname}, status={self.status})>"
    

def update_service_status(service_name: str, status: bool):
    """Update service status in database"""
    session = get_session()
    service = session.query(Service).filter(Service.Sname == service_name).first()
    if service:
        service.status = status
        session.commit()
    session.close()

def get_services():
    """Fetch all services from database"""
    session = get_session()
    services = session.query(Service).all()
    result = [
        {
            "name": service.Sname,
            "host": service.host,
            "port": service.port,
            "endPoint": service.endPoint
        }
        for service in services
    ]
    session.close()
    return result


Base.metadata.create_all(engine)
