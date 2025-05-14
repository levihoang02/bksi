from datetime import datetime

class Metric:
    def __init__(self, metric_name, chart_type, prom_type):
        self.metric_name = metric_name
        self.chart_type = chart_type
        self.prom_type = prom_type
        self.timestamp = datetime.utcnow()
    
    def to_dict(self):
        return {
            'metric_name': self.metric_name,
            'chart_type': self.chart_type,
            'prom_type': self.prom_type,
            'timestamp': self.timestamp
        }