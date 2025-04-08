from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import VARCHAR
import uuid
from .database import Base

class ServiceInstance(Base):
    __tablename__ = 'service_instances'

    id = Column(VARCHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    host = Column(String(255), nullable=True)
    port = Column(String(255), nullable=True)
    endPoint = Column(String(255), nullable=True)
    status = Column(Boolean, nullable=False, default=True)
    container_id = Column(String(255), nullable=True)

    service_id = Column(VARCHAR(36), ForeignKey('services.id'))
    service = relationship('Service', back_populates='service_instances')

    def __init__(self, host, port, endPoint, status=True, service_id=None, container_id= None):
        self.host = host
        self.port = port
        self.endPoint = endPoint
        self.status = status
        self.service_id = service_id
        self.container_id = container_id

    def __repr__(self):
        return f"<ServiceInstance(id={self.id}, host={self.host}, port={self.port}, status={self.status})>"
