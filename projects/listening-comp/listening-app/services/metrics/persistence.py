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
        start_date = pd.to_datetime(start_date) if start_date else None
        end_date = pd.to_datetime(end_date) if end_date else None

        # Traverse through the date-based directory structure
        for root, _, files in os.walk(self.base_path):
            for file in files:
                if file == f"{name}.jsonl":
                    filepath = os.path.join(root, file)
                    with open(filepath, "r") as f:
                        for line in f:
                            metric = json.loads(line)
                            timestamp = pd.to_datetime(metric["timestamp"])

                            # Filter by date range if provided
                            if (start_date and timestamp < start_date) or (end_date and timestamp > end_date):
                                continue

                            metrics.append(metric)

        return metrics
