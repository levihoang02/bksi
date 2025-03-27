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

class Report(Base):
    __tablename__ = 'reports'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    status = Column(Boolean, nullable=False)  # Ensure nullable=False
    created_date = Column(DateTime, nullable=True) 
    service_id = Column(CHAR(36, 'utf8mb4_bin'), ForeignKey('services.id'), nullable=False)
    service = relationship("Service")

    def __repr__(self):
        return f"<Report(service={self.service.Sname}, status={self.status}, date={self.created_date})>"

def add_report(name: str, created_date: DateTime, status: bool):
    session = get_session()
    # Find service by name
    service = session.query(Service).filter(Service.Sname == name).first()
    if not service:
        session.close()
        return
    
    # Create new report with service_id
    print(service.id)
    new_report = Report(
        service_id=service.id,
        created_date=created_date,
        status=status
    )
    session.add(new_report)
    session.commit()
    session.close()

def get_all_reports():
    session = get_session()
    reports = session.query(Report).options(joinedload(Report.service)).all()  # Eager load service
    session.close()
    return reports

def get_report_by_name(service_name: str):
    session = get_session()
    report = session.query(Report).join(Service).filter(Service.Sname == service_name).first()
    session.close()
    return report

def add_if_not_exist(service_name: str, created_date: DateTime):
    report = get_report_by_name(service_name)
    if not report:
        add_report(service_name, created_date)

Base.metadata.create_all(engine)
