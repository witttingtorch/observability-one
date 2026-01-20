# Root Cause Analysis (RCA) – Overview

## 1. Purpose

The Root Cause Analysis (RCA) engine in **Observability One** automatically identifies, ranks, and explains the most probable causes of incidents by correlating logs, metrics, and traces across distributed systems.

The primary goal is to **reduce Mean Time To Resolution (MTTR)** by transforming raw telemetry into actionable intelligence.

---

## 2. Design Principles

- Correlate signals instead of relying on single-metric alerts
- Provide probabilistic rankings, not absolute claims
- Back every conclusion with observable evidence
- Remain vendor-agnostic and OpenTelemetry-first
- Support incremental intelligence (rules → ML)

---

## 3. Inputs

### Telemetry Signals
- **Metrics**
  - Latency (p50 / p95 / p99)
  - Error rates
  - Throughput
  - Resource utilization
- **Traces**
  - Distributed spans
  - Critical path latency
  - Error propagation
- **Logs**
  - Structured errors
  - Stack traces
  - Warning patterns

### Contextual Signals
- Deployments
- Configuration changes
- Infrastructure events
- Feature flags (optional)

---

## 4. Canonical RCA Event Model

All inputs are normalized into a unified event structure:

  
This abstraction allows consistent correlation logic across heterogeneous data sources.

RCAEvent {
timestamp
service
signal_type (metric | log | trace)
severity
attributes
}
---

## 5. RCA Processing Pipeline
Telemetry Ingest
↓
Signal Normalization
↓
Anomaly Detection
↓
Cross-Signal Correlation
↓
Service Dependency Mapping
↓
Root Cause Ranking
↓
Explanation & Evidence


---

## 6. Anomaly Detection

### Baseline Methods
- Rolling averages
- Percentile deviation
- Z-score thresholds
- Seasonality-aware baselines (optional)

### Trigger Conditions
- Latency spikes
- Error-rate surges
- Resource saturation
- Traffic anomalies

Each anomaly is tagged with:
- Start time
- Duration
- Severity score

---

## 7. Correlation Engine

The correlation engine identifies causal relationships using:
- Temporal proximity
- Shared trace identifiers
- Service dependency adjacency
- Error propagation paths

**Example:**
> A spike in checkout-service latency is correlated with increased error logs in payment-service and downstream retry storms.

---

## 8. Service Dependency Graph

A directed dependency graph is constructed from distributed traces.

Uses:
- Blast radius estimation
- Upstream / downstream fault isolation
- Impact analysis

Edges are weighted by:
- Call frequency
- Latency contribution
- Error propagation rate

---

## 9. Root Cause Ranking

Each candidate root cause is scored using a weighted model:

RCA Score =
(Anomaly Severity × W1)

(Blast Radius × W2)

(Correlation Strength × W3)

(Change Proximity × W4)


Candidates are ranked by score to produce a prioritized RCA list.

---

## 10. RCA Output

### Root Cause Object
RootCause {
service
description
confidence_score
supporting_evidence
impacted_services
timeline
}


### Evidence Includes
- Sample logs
- Trace excerpts
- Metric charts
- Dependency graph snippets

---

## 11. Explainability

RCA results are written in human-readable form.

**Example Explanation:**
> Increased latency in checkout-service is most likely caused by timeouts in payment-service beginning three minutes after deployment v2.4.1. Evidence includes elevated error logs, increased span duration, and downstream retries.

---

## 12. Alerting & Automation

RCA outputs can:
- Enrich alerts
- Create incidents
- Trigger auto-remediation
- Notify Slack / PagerDuty / Webhooks

---

## 13. Operational Modes

- Real-time RCA during incidents
- Post-incident analysis
- Regression detection
- What-if simulations

---

## 14. Limitations & Guardrails

- RCA provides probable causes, not absolute truth
- Confidence scores are estimates
- Human validation is recommended for critical incidents

---

## 15. Future Enhancements

- Tail-based sampling integration
- ML-driven anomaly detection
- Causal inference models
- Change intelligence (CI/CD correlation)
- Natural language RCA summaries

---

## 16. Key Takeaway

> Observability One shifts teams from alert-driven firefighting to evidence-driven diagnosis.
