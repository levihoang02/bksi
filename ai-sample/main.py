from flask import Flask, request, jsonify, Response
import requests
import os
from services.monitoring import (
    monitor_request, 
    monitor_model_inference, 
    get_prometheus_metrics, 
    SystemMonitor
)
from kafka_utils.event import Event, EventType
from services.message import async_publish_event

from dotenv import load_dotenv
load_dotenv()
KAFKA_CLIENT_ID = os.getenv("KAFKA_CLIENT_ID")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC")

app = Flask(__name__)

# Environment variable for HuggingFace API Key
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# Define model endpoints
MODEL_ENDPOINTS = {
    "summary": "https://api-inference.huggingface.co/models/facebook/bart-large-cnn",
    "ner": "https://api-inference.huggingface.co/models/dbmdz/bert-large-cased-finetuned-conll03-english",
    "suggest_answer": "https://api-inference.huggingface.co/models/gpt2"  # Update if you have a better model
}

def query_hf_api(task, payload):
    model_url = MODEL_ENDPOINTS.get(task)
    if not model_url:
        raise ValueError(f"No endpoint configured for task '{task}'")

    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(model_url, headers=headers, json=payload)

    print(f"[DEBUG] status_code: {response.status_code}")
    print(f"[DEBUG] response.text: {response.text}")

    if response.status_code != 200:
        raise RuntimeError(f"Hugging Face API call failed with status code {response.status_code}: {response.text}")

    try:
        return response.json()
    except Exception as e:
        raise RuntimeError(f"Failed to decode JSON from Hugging Face API: {e}\nRaw response: {response.text}")

@app.route('/summary', methods=['POST'])
@monitor_request(method='POST', endpoint='/summary')
def summarize_text():
    """Summarization endpoint"""
    data = request.get_json()
    text = data.get("text", "")

    if not text:
        return jsonify({"error": "Missing 'text' field"}), 400
    summary_result = query_hf_api("summary", {"inputs": text})
    summary = summary_result[0]["summary_text"] if summary_result else "No summary available."
    try:
        event = Event(
            source=KAFKA_CLIENT_ID,
            op=EventType.SUMMARIZE,
            payload={
                "ticket_id": data.get("ticket_id"),
                "value": summary
            }
        )
        async_publish_event(KAFKA_TOPIC, event)
    except Exception as e:
        print(e)
        pass
    return jsonify({
        "summary": summary
    })

@app.route('/highlight', methods=['POST'])
@monitor_request(method='POST', endpoint='/highlight')
def highlight_entities():
    """Named Entity Recognition endpoint"""
    data = request.get_json()
    text = data.get("text", "")

    if not text:
        return jsonify({"error": "Missing 'text' field"}), 400

    ner_result = query_hf_api("ner", {"inputs": text})
    entities = list({item['word']: item['entity_group'] for item in ner_result}.items())
    
    try:
        event = Event(
            source=KAFKA_CLIENT_ID,
            op=EventType.NER,
            payload={
                "ticket_id": data.get("ticket_id"),
                "value": entities
            }
        )
        async_publish_event(KAFKA_TOPIC, event)
    except Exception as e:
        print(e)
        pass

    return jsonify({
        "entities": entities
    })

@app.route('/tag', methods=['POST'])
@monitor_request(method='POST', endpoint='/tag')
def suggest_answer():
    """Suggest an AI-generated answer based on the given question"""
    data = request.get_json()
    question = data.get("text", "")

    if not question:
        return jsonify({"error": "Missing 'text' field"}), 400

    generation_payload = {
        "inputs": question,
        "parameters": {
            "max_new_tokens": 100,
            "temperature": 0.7,
            "top_p": 0.9,
            "do_sample": True
        }
    }

    response = query_hf_api("suggest_answer", generation_payload)

    if isinstance(response, list) and "generated_text" in response[0]:
        answer = response[0]["generated_text"]
    else:
        answer = "No suggestion available."

    return jsonify({
        "suggested_answer": answer
    })


@app.route('/metrics', methods=['GET'])
def prometheus_metrics():
    """Expose Prometheus metrics"""
    data, content_type = get_prometheus_metrics()
    return Response(data, mimetype=content_type)

if __name__ == "__main__":
    app.run(debug=True)
