from fastapi import FastAPI
from fastapi.responses import StreamingResponse, Response
import json
import asyncio
from .processor.process import process
from .prometheus_metrics import get_prometheus_metrics

app = FastAPI()

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
    }

@app.get("/metrics")
async def metrics():
    metrics_data, content_type = get_prometheus_metrics()
    return Response(content=metrics_data, media_type=content_type)

@app.post("/process")
async def process_request(data: dict):
    """Sync request process"""
    try:
        result, _ = process(data)
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/stream")
async def stream_events(data: dict):
    """Streaming event by event service"""
    async def event_generator():
        try:
            result, _ = process(data)
            yield f"data: {json.dumps(result)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")