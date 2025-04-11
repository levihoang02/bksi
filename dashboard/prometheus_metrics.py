from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import psutil
import threading
import time

# Request counters
REQUEST_COUNT = Counter('report_request_total', 'Total number of requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('report_request_latency_seconds', 'Request latency in seconds', ['method', 'endpoint'])

# System metrics
SYSTEM_MEMORY = Gauge('report_memory_usage_bytes', 'Memory usage in bytes')
SYSTEM_CPU = Gauge('report_cpu_usage_percent', 'CPU usage percentage')

def get_metrics():
    """Generate latest metrics in Prometheus format"""
    return generate_latest(), CONTENT_TYPE_LATEST

class SystemMetricsMonitor:
    def __init__(self, interval=5):
        self.interval = interval
        self.process = psutil.Process()
        self._stop_event = threading.Event()
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)

    def start(self):
        """Start the monitoring thread"""
        self.monitor_thread.start()

    def stop(self):
        """Stop the monitoring thread"""
        self._stop_event.set()
        self.monitor_thread.join()

    def _monitor_loop(self):
        """Main monitoring loop"""
        while not self._stop_event.is_set():
            try:
                
                memory_info = self.process.memory_info()
                SYSTEM_MEMORY.set(memory_info.rss)

                cpu_percent = self.process.cpu_percent()
                SYSTEM_CPU.set(cpu_percent)

            except Exception as e:
                print(f"Error updating system metrics: {e}")

            time.sleep(self.interval)

system_monitor = SystemMetricsMonitor()