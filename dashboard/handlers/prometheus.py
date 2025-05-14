import uuid
import os

PROMETHEUS_UID = os.getenv("PROMETHEUS_UID")

def generate_dashboard_json_from_metrics(metrics: list[dict], job_name: str) -> dict:
    dashboard_uid = str(uuid.uuid4())[:8]
    dashboard_title = f"{job_name.capitalize()} Metrics Dashboard"

    panels = []
    for i, metric in enumerate(metrics):
        panel_id = i + 1
        chart_type = metric["chart_type"]
        metric_name = metric["metric_name"]
        prom_type = metric.get("prom_type", "")
        if (chart_type == "heatmap" or prom_type == "Histogram") and not metric_name.endswith("_bucket"):
            metric_name += "_bucket"
        panel = {
            "type": chart_type,
            "title": metric["metric_name"],
            "targets": [{
                "expr": f'{metric_name}{{job="{job_name}"}}',
                "refId": "A"
            }],
            "gridPos": {
                "h": 8,
                "w": 12,
                "x": (i % 2) * 12,
                "y": (i // 2) * 8
            },
            "id": panel_id,
            "datasource": {"type": "prometheus", "uid": f'{PROMETHEUS_UID}'},
        }

        panels.append(panel)

    dashboard = {
        "uid": dashboard_uid,
        "title": dashboard_title,
        "timezone": "browser",
        "schemaVersion": 38,
        "version": 1,
        "refresh": "10s",
        "time": {
            "from": "now-1h",
            "to": "now"
        },
        "panels": panels
    }

    return {
        "dashboard": dashboard,
        "overwrite": True
    }