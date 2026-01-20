# Architecture

## Core Components
- OTEL Collector (ingest)
- Ingest API (auth, validation)
- Processing Engine (normalization, correlation)
- RCA Engine (anomaly detection, ranking)
- Exporters (vendor-specific)

## RCA Flow
1. Detect anomaly
2. Correlate traces, logs, metrics
3. Identify probable root cause
4. Rank by impact
