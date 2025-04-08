from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import VARCHAR
import uuid
from .database import Base

from .serviceInstance import ServiceInstance

class Service(Base):
    __tablename__ = 'services'

    id = Column(VARCHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    Sname = Column(String(255), nullable=False, unique=True)

    service_instances = relationship('ServiceInstance', back_populates='service')

    def __init__(self, Sname):
        self.Sname = Sname

    def __repr__(self):
        return f"<Service(id={self.id}, Sname={self.Sname})>"

    def add_service_instance(self, session, host, port, endPoint):
        service_instance = ServiceInstance(host=host, port=port, endPoint=endPoint, service_id=self.id)
        session.add(service_instance)
        session.commit()
        return service_instance