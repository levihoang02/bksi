import threading
import time
from datetime import datetime
from schemas.healthchecker import HealthChecker
from utils.config import Config
from utils.logger import setup_logger

config = Config()
logger = setup_logger('healthcheck-service')

if __name__ == "__main__":
   healthcheck = HealthChecker(logger=logger, delay=30)
   healthcheck.run()
