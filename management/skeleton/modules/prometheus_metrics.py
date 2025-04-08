from prometheus_client import Counter, Histogram

REQUEST_SUCCESS = Counter('request_success_total', 'Sucessful request')
REQUEST_FAILURE = Counter('request_failure_total', 'Failed request')

PROCESS_TIME = Histogram('process_duration_seconds', 'Processing Time')