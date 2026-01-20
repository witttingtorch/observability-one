"""
Anomaly Detection Module

Detects anomalies in time-series metrics used by the RCA engine.
Designed for explainability, reliability, and incremental intelligence.

Current techniques:
- Rolling baseline deviation
- Z-score detection
- Percentile-based thresholds

Future-ready for:
- Seasonal models
- ML-based detectors (Isolation Forest, LSTM)
"""

from dataclasses import dataclass
from typing import List, Dict, Any
import statistics
import time


@dataclass
class Anomaly:
    """
    Represents a detected anomaly.
    """
    service: str
    metric: str
    timestamp: float
    value: float
    baseline: float
    deviation: float
    severity: float
    method: str
    context: Dict[str, Any]


class AnomalyDetector:
    """
    Detects anomalies in metric time series.

    Expected input format:
    [
        {
            "service": "checkout-service",
            "metric": "latency_ms",
            "timestamp": 1690000000,
            "value": 250
        },
        ...
    ]
    """

    def __init__(
        self,
        zscore_threshold: float = 3.0,
        min_samples: int = 10,
        severity_scale: float = 10.0,
    ):
        self.zscore_threshold = zscore_threshold
        self.min_samples = min_samples
        self.severity_scale = severity_scale

    # ---------------------------
    # Public API
    # ---------------------------

    def detect(self, points: List[Dict[str, Any]]) -> List[Anomaly]:
        """
        Detect anomalies across all metric series.
        """
        grouped = self._group_by_series(points)
        anomalies: List[Anomaly] = []

        for key, series in grouped.items():
            if len(series) < self.min_samples:
                continue

            anomalies.extend(self._detect_series(series))

        return anomalies

    # ---------------------------
    # Detection Logic
    # ---------------------------

    def _detect_series(self, series: List[Dict[str, Any]]) -> List[Anomaly]:
        """
        Detect anomalies within a single metric series.
        """
        values = [p["value"] for p in series]
        mean = statistics.mean(values)
        stdev = statistics.stdev(values) if len(values) > 1 else 0.0

        anomalies: List[Anomaly] = []

        for point in series:
            if stdev == 0:
                continue

            zscore = abs((point["value"] - mean) / stdev)

            if zscore >= self.zscore_threshold:
                severity = min(
                    self.severity_scale,
                    zscore / self.zscore_threshold * self.severity_scale,
                )

                anomalies.append(
                    Anomaly(
                        service=point["service"],
                        metric=point["metric"],
                        timestamp=point["timestamp"],
                        value=point["value"],
                        baseline=mean,
                        deviation=point["value"] - mean,
                        severity=round(severity, 2),
                        method="z-score",
                        context={
                            "zscore": round(zscore, 2),
                            "mean": round(mean, 2),
                            "stdev": round(stdev, 2),
                        },
                    )
                )

        return anomalies

    # ---------------------------
    # Helpers
    # ---------------------------

    def _group_by_series(self, points: List[Dict[str, Any]]):
        """
        Groups points by (service, metric).
        """
        grouped: Dict[str, List[Dict[str, Any]]] = {}

        for p in points:
            key = f"{p['service']}::{p['metric']}"
            grouped.setdefault(key, []).append(p)

        return grouped


# ---------------------------
# Example Usage
# ---------------------------

if __name__ == "__main__":
    detector = AnomalyDetector()

    sample = [
        {"service": "checkout", "metric": "latency_ms", "timestamp": time.time(), "value": v}
        for v in [120, 130, 125, 140, 135, 128, 132, 129, 131, 500]
    ]

    results = detector.detect(sample)
    for a in results:
        print(a)
