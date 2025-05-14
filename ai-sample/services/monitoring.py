from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from Flask import Response
import time
import threading
import psutil
import os
import sys
import functools

try:
    import pynvml
    pynvml.nvmlInit()
    NVML_AVAILABLE = True
    GPU_HANDLE = pynvml.nvmlDeviceGetHandleByIndex(0)
except Exception:
    NVML_AVAILABLE = False
    GPU_HANDLE = None

# ------------------- METRICS DEFINITIONS ------------------- #

# Request metrics
REQUEST_COUNT = Counter('ai_request_total', 'Total number of AI inference requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('ai_request_latency_seconds', 'Latency of AI inference requests in seconds', ['method', 'endpoint'])

# Inference metrics
INFERENCES_TOTAL = Counter('model_inferences_total', 'Total number of model inferences')
INFERENCE_ERRORS = Counter('model_inference_errors_total', 'Total number of inference errors')
MODEL_RESPONSE_TIME = Histogram('model_response_time_seconds', 'Time taken per inference')
BATCH_SIZE = Histogram('model_batch_size', 'Batch size of input')
INPUT_DATA_SIZE = Histogram('model_input_data_size_bytes', 'Input data size in bytes')
OUTPUT_DATA_SIZE = Histogram('model_output_data_size_bytes', 'Output data size in bytes')
INPUT_TOKENS = Histogram('model_input_tokens_total', 'Number of tokens in the input', buckets=[10, 50, 100, 200, 500, 1000, 2000, 5000])
OUTPUT_TOKENS = Histogram('model_output_tokens_total', 'Number of tokens in the output', buckets=[10, 50, 100, 200, 500, 1000, 2000, 5000])

# Accuracy / Loss
MODEL_ACCURACY = Gauge('ai_model_accuracy', 'Accuracy of the AI model')
MODEL_LOSS = Gauge('ai_model_loss', 'Current loss of the model')

# System metrics
MEMORY_USAGE = Gauge('ai_memory_usage_bytes', 'Memory usage in bytes')
CPU_USAGE = Gauge('ai_cpu_usage_percent', 'CPU usage percentage')
GPU_MEMORY_USAGE = Gauge('ai_gpu_memory_usage_bytes', 'GPU memory usage in bytes')
GPU_UTILIZATION = Gauge('ai_gpu_utilization_percent', 'GPU utilization percentage')


# ------------------- SYSTEM MONITOR ------------------- #

class SystemMonitor:
    def __init__(self, interval=5):
        self.interval = interval
        self.process = psutil.Process(os.getpid())
        self.process.cpu_percent(interval=None)  # Prime CPU measurement
        self._stop_event = threading.Event()
        self.thread = threading.Thread(target=self._run, daemon=True)

    def start(self):
        self.thread.start()

    def stop(self):
        self._stop_event.set()
        self.thread.join()

    def _run(self):
        while not self._stop_event.is_set():
            try:
                MEMORY_USAGE.set(self.process.memory_info().rss)
                CPU_USAGE.set(self.process.cpu_percent())

                if NVML_AVAILABLE:
                    mem = pynvml.nvmlDeviceGetMemoryInfo(GPU_HANDLE)
                    GPU_MEMORY_USAGE.set(mem.used)
                    GPU_UTILIZATION.set(pynvml.nvmlDeviceGetUtilizationRates(GPU_HANDLE).gpu)
            except Exception as e:
                print(f"Error collecting system metrics: {e}")
            time.sleep(self.interval)


# ------------------- DECORATORS ------------------- #

def monitor_request(method, endpoint):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            status = '200'
            try:
                result = func(*args, **kwargs)
                return result
            except Exception:
                status = '500'
                raise
            finally:
                latency_seconds = time.time() - start_time
                REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()
                REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(latency_seconds)
        return wrapper
    return decorator


def monitor_model_inference():
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            INFERENCES_TOTAL.inc()
            start_time = time.time()

            input_data = args[0] if args else kwargs.get('input')
            batch_size = len(input_data) if hasattr(input_data, '__len__') else 1
            input_size = _estimate_size(input_data)
            BATCH_SIZE.observe(batch_size)
            INPUT_DATA_SIZE.observe(input_size)

            try:
                output = func(*args, **kwargs)
                response_time = time.time() - start_time
                MODEL_RESPONSE_TIME.observe(response_time)

                output_size = _estimate_size(output)
                OUTPUT_DATA_SIZE.observe(output_size)

                return output
            except Exception as e:
                INFERENCE_ERRORS.inc()
                raise e
        return wrapper
    return decorator


def monitor_model_tokens(tokenizer):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            input_data = args[0] if args else kwargs.get('input')

            try:
                input_tokens = tokenizer(input_data)
                token_count = _extract_token_count(input_tokens)
                if token_count:
                    INPUT_TOKENS.observe(token_count)
            except Exception:
                pass

            try:
                output = func(*args, **kwargs)
                try:
                    output_tokens = tokenizer(output)
                    token_count = _extract_token_count(output_tokens)
                    if token_count:
                        OUTPUT_TOKENS.observe(token_count)
                except Exception:
                    pass
                return output
            except Exception as e:
                raise e
        return wrapper
    return decorator

def track_model_accuracy():
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            try:
                if isinstance(result, dict) and 'accuracy' in result:
                    MODEL_ACCURACY.set(result['accuracy'])
                elif isinstance(result, Response):
                    json_data = result.get_json()
                    if json_data and 'accuracy' in json_data:
                        MODEL_ACCURACY.set(json_data['accuracy'])
            except Exception:
                pass
            return result
        return wrapper
    return decorator

def track_model_loss():
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            try:
                if isinstance(result, dict) and 'loss' in result:
                    MODEL_LOSS.set(result['loss'])
                elif isinstance(result, Response):
                    json_data = result.get_json()
                    if json_data and 'loss' in json_data:
                        MODEL_ACCURACY.set(json_data['loss'])
            except Exception:
                pass
            return result
        return wrapper
    return decorator

def track_output_metrics(metric_names: list[str], metric_registry: dict[str, Gauge]):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            try:
                output = None
                if isinstance(result, dict):
                    output = result
                elif isinstance(result, Response):
                    output = result.get_json()

                if output:
                    for name in metric_names:
                        if name in output and name in metric_registry:
                            metric_registry[name].set(output[name])
            except Exception as e:
                print(f"[track_output_metrics] Failed to track metrics: {e}")

            return result
        return wrapper
    return decorator



# ------------------- HELPERS ------------------- #

def _estimate_size(data):
    try:
        return sys.getsizeof(data)
    except Exception:
        return 0

def _extract_token_count(tokenized_output):
    if isinstance(tokenized_output, dict):
        if 'input_ids' in tokenized_output:
            return len(tokenized_output['input_ids'])
    elif hasattr(tokenized_output, '__len__'):
        return len(tokenized_output)
    return None

def get_prometheus_metrics():
    return generate_latest(), CONTENT_TYPE_LATEST
