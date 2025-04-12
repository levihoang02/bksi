from fastapi import FastAPI
from fastapi.responses import StreamingResponse, Response
import json
import asyncio
from .processor.process import process
from .prometheus_metrics import REQUEST_SUCCESS, REQUEST_FAILURE, PROCESS_TIME, get_metrics

app = FastAPI()

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
    }

@app.get("/metrics")
async def metrics():
    metrics_data, content_type = get_metrics()
    return Response(content=metrics_data, media_type=content_type)

@app.post("/process")
async def process_request(data: dict):
    """Sync request process"""
    try:
        with PROCESS_TIME.time():
            result, _ = process(data)
        REQUEST_SUCCESS.inc()
        return {"status": "success", "result": result}
    except Exception as e:
        REQUEST_FAILURE.inc()
        return {"status": "error", "message": str(e)}

@app.get("/stream")
async def stream_events(data: dict):
    """Streaming event by event service"""
    async def event_generator():
        try:
            with PROCESS_TIME.time():
                result, _ = process(data)
            REQUEST_SUCCESS.inc()
            yield f"data: {json.dumps(result)}\n\n"
        except Exception as e:
            REQUEST_FAILURE.inc()
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")