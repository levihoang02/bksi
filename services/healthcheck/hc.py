import threading
import requests
import time
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from schemas.service import get_services, update_service_status
from utils.config import Config
from utils.logger import setup_logger

config = Config()
logger = setup_logger('healthcheck-service')

def send_alert_email(service_name: str, error_message: str):
    """Send alert email to admin when service is down"""
    sender_email = config.SMTP_EMAIL
    sender_password = config.SMTP_PASSWORD
    receiver_email = config.ADMIN_EMAIL
    
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = f"Service Alert: {service_name} is DOWN"
    
    body = f"""
    Service {service_name} is currently experiencing issues.
    Error: {error_message}
    Time: {datetime.utcnow()}
    """
    message.attach(MIMEText(body, "plain"))
    
    try:
        with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(message)
    except Exception as e:
        print(f"Failed to send alert email: {str(e)}")

def check_service_health(service):
    """Check if a service is healthy and update status"""
    try:
        url = f"http://{service['host']}:{service['port']}/health"
        logger.info('Checking service health', extra={
            "timestamp": datetime.now().isoformat(),
            'service_name': service['name'],
            'url': url
        })
        
        response = requests.get(url, timeout=5)
        is_healthy = response.status_code == 200 and response.json().get('status') == 'healthy'
        
        update_service_status(service['name'], is_healthy)
        
        if not is_healthy:
            error_msg = f"Service returned status code: {response.status_code}"
            logger.error('Service health check failed', extra={
                "timestamp": datetime.now().isoformat(),
                'service_name': service['name'],
                'status_code': response.status_code,
                'error': error_msg
            })
            send_alert_email(service['name'], error_msg)
        else:
            logger.info('Service health check successful', extra={
                "timestamp": datetime.now().isoformat(),
                'service_name': service['name'],
                'status_code': response.status_code
            })
            
        return is_healthy
            
    except Exception as e:
        error_msg = str(e)
        logger.error('Service health check failed with exception', extra={
            "timestamp": datetime.now().isoformat(),
            'service_name': service['name'],
            'error': error_msg,
            'exception': type(e).__name__
        }, exc_info=True)
        
        update_service_status(service['name'], False)
        send_alert_email(service['name'], error_msg)
        return False

def health_check_worker():
    """Worker function to periodically check service health"""
    while True:
        services = get_services()
        for service in services:
            is_healthy = check_service_health(service)
            status = "UP" if is_healthy else "DOWN"
            print(f"Health check for {service['name']}: {status}")
        time.sleep(30)  # Check every 30 seconds

def run_health_checker():
    """Start the health check worker in a background thread"""
    health_check_thread = threading.Thread(target=health_check_worker)
    health_check_thread.daemon = True
    health_check_thread.start()

if __name__ == "__main__":
   health_check_worker()
