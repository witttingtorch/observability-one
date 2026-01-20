"""
Observability One – Ingest API

Enterprise-grade telemetry ingest service.
Receives logs, metrics, traces, normalizes them,
runs RCA intelligence, and prepares data for export.

Design goals:
- OpenTelemetry-first
- Vendor-neutral
- Multi-tenant ready
- Secure & observable
"""

from fastapi import FastAPI, Request, HTTPException, Header
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import time
import logging

from src.processors.anomaly import AnomalyDetector
from src.processors.correlation import CorrelationEngine
from src.processors.rca import RCAEngine

# --------------------------------------------------
# App & Logging
# --------------------------------------------------

app = FastAPI(
    title="Observability One Ingest API",
    version="1.0.0",
    description="Unified telemetry ingest & RCA intelligence service",
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("observability-ingest")

# --------------------------------------------------
# Intelligence Engines
# --------------------------------------------------

anomaly_detector = AnomalyDetector()
correlation_engine = CorrelationEngine()
rca_engine = RCAEngine()

# --------------------------------------------------
# Models
# --------------------------------------------------

class TelemetryRecord(BaseModel):
    service: str
    timestamp: float
    attributes: Dict[str, Any] = {}
    trace_id: Optional[str] = None


class MetricRecord(TelemetryRecord):
    metric: str
    value: float


class LogRecord(TelemetryRecord):
    message: str
    severity: Optional[str] = "INFO"


class TraceRecord(TelemetryRecord):
    span_id: str
    duration_ms: Optional[float] = None


class IngestPayload(BaseModel):
    metrics: List[MetricRecord] = []
    logs: List[LogRecord] = []
    traces: List[TraceRecord] = []


# --------------------------------------------------
# Security & Tenant Resolution
# --------------------------------------------------

def authenticate(api_key: Optional[str]) -> str:
    """
    Resolve tenant from API key.
    Replace with real auth / IAM later.
    """
    if not api_key:
        raise HTTPException(status_code=401, detail="Missing API key")

    # Placeholder tenant mapping
    return "default-tenant"


# --------------------------------------------------
# Routes
# --------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok", "timestamp": time.time()}


@app.post("/ingest")
def ingest(
    payload: IngestPayload,
    request: Request,
    x_api_key: Optional[str] = Header(None),
):
    """
    Main telemetry ingest endpoint.
    """
    tenant = authenticate(x_api_key)

    logger.info(
        "Received ingest request | tenant=%s metrics=%d logs=%d traces=%d",
        tenant,
        len(payload.metrics),
        len(payload.logs),
        len(payload.traces),
    )

    # ----------------------------
    # Normalize telemetry
    # ----------------------------

    metrics = [
        {
            "service": m.service,
            "metric": m.metric,
            "value": m.value,
            "timestamp": m.timestamp,
            "attributes": m.attributes,
        }
        for m in payload.metrics
    ]

    logs = [
        {
            "service": l.service,
            "message": l.message,
            "severity": l.severity,
            "timestamp": l.timestamp,
            "trace_id": l.trace_id,
            "attributes": l.attributes,
        }
        for l in payload.logs
    ]

    traces = [
        {
            "service": t.service,
            "span_id": t.span_id,
            "trace_id": t.trace_id,
            "timestamp": t.timestamp,
            "duration_ms": t.duration_ms,
            "attributes": t.attributes,
        }
        for t in payload.traces
    ]

    # ----------------------------
    # Intelligence Pipeline
    # ----------------------------

    anomalies = anomaly_detector.detect(metrics)

    correlation_groups = correlation_engine.correlate(
        anomalies=[a.__dict__ for a in anomalies],
        logs=logs,
        traces=traces,
        metrics=metrics,
    )

    root_causes = rca_engine.analyze(correlation_groups)

    # ----------------------------
    # Response
    # ----------------------------

    return {
        "tenant": tenant,
        "ingested": {
            "metrics": len(metrics),
            "logs": len(logs),
            "traces": len(traces),
        },
        "anomalies_detected": len(anomalies),
        "correlation_groups": len(correlation_groups),
        "root_causes": [rc.__dict__ for rc in root_causes],
    }


# --------------------------------------------------
# Local Dev Entrypoint
# --------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
