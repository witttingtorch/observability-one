# Observability One – Enterprise Edition

Enterprise-grade observability platform for logs, metrics, traces, APM, and automated Root Cause Analysis (RCA).

## Enterprise Capabilities
- OpenTelemetry-first ingestion (OTLP HTTP/gRPC)
- Vendor-neutral canonical telemetry schema
- Automated RCA (correlation, anomaly detection, blast-radius analysis)
- Secure multi-tenant architecture
- Role-Based Access Control (RBAC)
- Enterprise integrations (Datadog, New Relic, Splunk, CloudWatch, Azure Monitor, Instana, SolarWinds)
- Cloud-native & on‑prem deployment

## Architecture
Agent → OTEL Gateway → Ingest API → Processing & RCA → Exporters → Vendor Backends

## Quick Start
```bash
docker-compose up
```

## Security
- API keys via environment variables
- TLS termination supported
- Audit logging enabled

## License
MIT
