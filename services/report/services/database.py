from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import urllib.parse
Base = declarative_base()

from utils.config import Config

config = Config()

connection_string = f"mysql+pymysql://{config.DATABASE_USER}:{config.DATABASE_PASSWORD}@{config.DATABASE_HOST}:{config.DATABASE_PORT}/{config.DATABASE_NAME}?charset=utf8mb4"
print(connection_string)
engine = create_engine(connection_string)

Session = sessionmaker(bind=engine)

def get_session():
    return Session()