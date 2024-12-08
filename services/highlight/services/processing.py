import requests
from datetime import datetime
from utils.config import Config
from services.kafka_producer import send_report
import logging

config = Config()
logger = logging.getLogger(__name__)

def process_data(data):
    """
    Process the incoming data by calling external NER service and send report
    """
    try:
        request_time = datetime.now()
        payload = data.get('payload', '')
        id = data.get('id', '')
        
        # Make request to external NER service
        response = requests.post(
            config.NER_SERVICE_URL,
            json={'payload': payload, 'id': id},
            timeout=180
        )
        
        processing_time = (datetime.now() - request_time).total_seconds()
        
        # Prepare report data
        report_data = {
            "service": "ServiceHighlight",
            "timestamp": request_time.isoformat(),
            "processing_time": processing_time,
            "status": response.status_code == 200,
            "error": None
        }
        
        if response.status_code == 200:
            result = response.json()
            # Send success report
            send_report(report_data)
            return result, 200
        else:
            error_msg = f"NER service error: {response.status_code}"
            report_data["error"] = error_msg
            # Send error report
            send_report(report_data)
            logger.error(error_msg)
            return {"error": error_msg}, response.status_code
            
    except Exception as e:
        error_msg = str(e)
        report_data = {
            "service": "highlight",
            "timestamp": datetime.now().isoformat(),
            "processing_time": None,
            "status": "error",
            "error": error_msg
        }
        send_report(report_data)
        logger.error(f"Processing error: {error_msg}")
        return {"error": error_msg}, 500
