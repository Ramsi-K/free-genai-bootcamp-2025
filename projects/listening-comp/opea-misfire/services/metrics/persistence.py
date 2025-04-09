import os
import json
from datetime import datetime
import pandas as pd


class MetricsPersistence:
    def __init__(self, base_path="/shared/data/metrics"):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)

    def store_metric(self, name, value, labels=None):
        """Store individual metric with timestamp"""
        timestamp = datetime.now().isoformat()
        metric_data = {
            "timestamp": timestamp,
            "value": value,
            "labels": labels or {},
        }

        # Store in date-based directory structure
        date = datetime.now().strftime("%Y/%m/%d")
        path = os.path.join(self.base_path, date)
        os.makedirs(path, exist_ok=True)

        filename = f"{name}.jsonl"
        filepath = os.path.join(path, filename)

        with open(filepath, "a") as f:
            f.write(json.dumps(metric_data) + "\n")

    def get_metrics(self, name, start_date=None, end_date=None):
        """Retrieve metrics for analysis"""
        metrics = []
        # Implementation for reading stored metrics
