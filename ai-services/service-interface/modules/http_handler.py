from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, Response
import json
from transformers import AutoTokenizer
from .process import process
from .prometheus_metrics import (
    monitor_request,
    track_model_accuracy,
    track_model_loss,
    monitor_model_inference,
    monitor_model_tokens
)
from .prometheus_metrics import get_prometheus_metrics

tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

app = FastAPI()

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    metrics_data, content_type = get_prometheus_metrics()
    return Response(content=metrics_data, media_type=content_type)

# Apply decorators to the process_request endpoint
@app.post("/process")
@monitor_request(method="POST", endpoint="/process")
@track_model_accuracy()
@track_model_loss()
@monitor_model_inference()
@monitor_model_tokens(tokenizer)  # Using the tokenizer here
async def process_request(data: dict):
    """Sync request process"""
    try:
        result, _ = process(data)
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Apply decorators to the stream_events endpoint
@app.get("/stream")
@monitor_request(method="GET", endpoint="/stream")
@monitor_model_inference()
@monitor_model_tokens(tokenizer)  # Using the tokenizer here as well
async def stream_events(data: dict):
    """Streaming event by event service"""
    async def event_generator():
        try:
            result, _ = process(data)
            yield f"data: {json.dumps(result)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
