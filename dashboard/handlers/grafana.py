import requests
import os

GRAFANA_URL = os.getenv("GRAFANA_URL")
GRAFANA_API_KEY = os.getenv("GRAFANA_KEY")
AUTH_HEADER = f"Bearer {GRAFANA_API_KEY}"

def create_or_update_dashboard_on_grafana(dashboard_json: dict):
    url = f"http://{GRAFANA_URL}/api/dashboards/db"
    print(f"Grafana {url}")
    print(AUTH_HEADER)
    headers = {
        "Authorization": AUTH_HEADER,
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, json=dashboard_json)

    if response.status_code not in [200, 202]:
        raise Exception(f"Grafana API Error: {response.status_code} - {response.text}")

    return response.json()
