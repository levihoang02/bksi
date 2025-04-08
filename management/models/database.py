from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Database:
    def __init__(self, db_url, pool_size=5, max_overflow=10, pool_timeout=30, pool_recycle=3600):
        self.db_url = db_url
        self.engine = create_engine(
            db_url,
            poolclass=QueuePool,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_timeout=pool_timeout,
            pool_recycle=pool_recycle
        )
        self.Session = sessionmaker(bind=self.engine, autocommit= False)

    def create_session(self):
        return self.Session()

    def create_all(self):
        Base.metadata.create_all(self.engine)


