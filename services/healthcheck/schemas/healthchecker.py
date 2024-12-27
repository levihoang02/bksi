import redis
from utils.config import Config
import time
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests

config = Config()

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

class HealthChecker:
    def __init__(self, logger=None, delay=30, pattern = "*:instances:*"):
        print("Initializing healthcheck ...")
        try:
            print("Establising redis connection...")
            self.redis_client = redis.Redis(
                host=config.REDIS_HOST,
                port=6379, 
                decode_responses=True  # Add this to avoid manual decoding
            )
            # Test connection
            ping = self.redis_client.ping()
            if(ping):
                print("Connected to redis!")
        except redis.ConnectionError as e:
            if logger:
                logger.error(f"Failed to connect to Redis: {e}")
            raise
        self.instances = dict()
        self.logger = logger
        self.delay = delay
        self.pattern = pattern
        self.keys = []
        self._load_instances()
        self.pubsub = self.redis_client.pubsub()
        self.subscribe_to_changes()
        print("Instances: ")
        print(self.keys)
        print("Instances' info")
        print(self.instances)
        print("Finish intialize!")
        
    def subscribe_to_changes(self):
        """Subscribe to Redis keyspace notifications for instance changes"""
        # Enable keyspace notifications if not already enabled
        self.redis_client.config_set('notify-keyspace-events', 'KEA')
        
        self.pubsub.psubscribe(**{
            '__keyspace@0__:' + self.pattern: self._handle_pubsub_message
        })
        # Start listening thread
        self.pubsub_thread = self.pubsub.run_in_thread(sleep_time=0.1)
        
    def _handle_pubsub_message(self, message):
        """Handler for pubsub messages"""
        try:
            if message['type'] == 'pmessage':
                # Extract the key from the channel
                channel = message['channel'].decode('utf-8')
                key = channel.split(':')[-1]
                self.handle_instance_change(key)
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error handling pubsub message: {e}")

    def handle_instance_change(self, key: str):
        """Update local cache when an instance is modified in Redis"""
        try:
            # Check if key still exists
            if not self.redis_client.exists(key):
                if key in self.instances:
                    del self.instances[key]
                if key in self.keys:
                    self.keys.remove(key)
                if self.logger:
                    self.logger.info(f"Instance removed: {key}")
                return

            # Update instance data
            fields = self.redis_client.hgetall(key)
            if fields:
                self.instances[key] = {
                    "name": key,
                    "host": fields.get(b"host", b"unknown").decode('utf-8'),
                    "port": fields.get(b"port", b"unknown").decode('utf-8'),
                    "endpoint": fields.get(b"endpoint", b"unknown").decode('utf-8'),
                    "status": fields.get(b"status", b"unknown").decode('utf-8') == "true",
                }
                if key not in self.keys:
                    self.keys.append(key)
                if self.logger:
                    self.logger.info(f"Instance updated: {key}")

        except redis.RedisError as e:
            if self.logger:
                self.logger.error(f"Failed to handle instance change for {key}: {e}")
        
    def _load_instances(self):
        """Loads all Redis keys matching the pattern into self.instances."""
        print("Fetching instances...")
        try:
            cursor = 0
            while True:
                cursor, keys = self.redis_client.scan(cursor=cursor, match=self.pattern)
                self.keys.extend(keys)
                if cursor == 0:
                    break
            # self.keys = [key.decode('utf-8') for key in self.keys]
            for instance in self.keys:
                fields = self.redis_client.hgetall(instance)
                if fields:
                    self.instances[instance] = {
                        "name": instance,
                        "host": fields.get("host") or "unknown",
                        "port": fields.get("port") or "unknown",
                        "endpoint": fields.get("endpoint") or "unknown",
                        "status": fields.get("status", "false") == "true",
                    }
        except redis.ConnectionError as e:
            if self.logger:
                self.logger.error(f"Redis connection failed: {e}")
            raise
    
    def check_service_health(self, instance):
        try:
            url = f"http://{instance['host']}:{instance['port']}/health"
            self.logger.info('Checking service health', extra={
                "timestamp": datetime.now().isoformat(),
                'service_name': instance['name'],
                'url': url
            })
            print(f"Checking health of {url}")
            response = requests.get(url, timeout=10)
            is_healthy = response.status_code == 200 and response.json().get('status') == 'healthy'
            
            if(is_healthy != instance["status"]):
                self.update_service_status(instance["name"], is_healthy)
            
            if not is_healthy:
                error_msg = f"Service returned status code: {response.status_code}"
                self.logger.error('Service health check failed', extra={
                    "timestamp": datetime.now().isoformat(),
                    'service_name': instance['name'],
                    'status_code': response.status_code,
                    'error': error_msg
                })
                send_alert_email(instance['name'], error_msg)
            else:
                self.logger.info('Service health check successful', extra={
                    "timestamp": datetime.now().isoformat(),
                    'service_name': instance['name'],
                    'status_code': response.status_code
                })
                
            return is_healthy
                
        except Exception as e:
            error_msg = str(e)
            self.logger.error('Service health check failed with exception', extra={
                "timestamp": datetime.now().isoformat(),
                'service_name': instance['name'],
                'error': error_msg,
                'exception': type(e).__name__
            }, exc_info=True)
            
            if(instance["status"] != False):
                self.update_service_status(instance=instance['name'], status=False)
            send_alert_email(instance['name'], error_msg)
            return False
        
    def update_service_status(self, instance, status):
        self.redis_client.hset(instance, "status", "true" if status else "false")
        
    def run(self):
        print("Starting up healtcheck...")
        try:
            while True:
                try:
                    # Process any pending Redis notifications
                    message = self.pubsub.get_message()
                    if message and message['type'] == 'pmessage':
                        # Extract the key from the channel
                        channel = message['channel'].decode('utf-8')
                        key = channel.split(':')[-1]
                        self.handle_instance_change(key)

                    # Regular health checks
                    for instance in self.instances.values():
                        self.check_service_health(instance)
                    
                    time.sleep(self.delay)

                except Exception as e:
                    if self.logger:
                        self.logger.error(f"Error in main loop: {e}")
                    time.sleep(self.delay)
        except KeyboardInterrupt:
            print("\nShutting down healthcheck...")
            self.destroy()
    
    def destroy(self):
        try:
            if hasattr(self, 'pubsub_thread'):
                self.pubsub_thread.stop()
            if hasattr(self, 'pubsub'):
                self.pubsub.close()
            if hasattr(self, 'redis_client'):
                self.redis_client.close()
        except Exception as e:
            self.destroy()
            if self.logger:
                self.logger.error(f"Error during cleanup: {e}")
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        try:
            if hasattr(self, 'pubsub_thread'):
                self.pubsub_thread.stop()
                self.pubsub_thread = None
            if hasattr(self, 'pubsub'):
                self.pubsub.unsubscribe()
                self.pubsub.close()
                self.pubsub = None
            if hasattr(self, 'redis_client'):
                self.redis_client.close()
                self.redis_client = None
        except:
            pass       
        
        