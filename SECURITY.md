# Security Policy

## 1. Overview

Security is a core design principle of **Observability One**.

This project handles telemetry that may include operational, infrastructure,
and application-level data. As such, we take security, privacy, and responsible
disclosure seriously.

This document outlines how to report vulnerabilities and how security is
handled within the project.

---

## 2. Supported Versions

Security fixes are applied to the **latest released version** and the `main`
branch.

| Version | Supported |
|--------|-----------|
| main   | ✅ |
| older releases | ❌ |

---

## 3. Reporting a Vulnerability

If you discover a security vulnerability, **do not open a public issue**.

### Responsible Disclosure
Please report vulnerabilities privately using one of the following methods:

- GitHub Security Advisories (preferred)
- Direct contact with the maintainers

When reporting, include:
- A detailed description of the issue
- Steps to reproduce
- Potential impact
- Any known mitigations

We aim to acknowledge reports within **48 hours** and provide updates as the
issue is investigated.

---

## 4. Scope

### In Scope
- Authentication & authorization logic
- Telemetry ingest endpoints
- Data isolation between tenants
- Exporter integrations
- Secrets handling
- CI/CD pipeline security
- Dependency vulnerabilities

### Out of Scope
- Misconfiguration of third-party observability platforms
- Issues caused by unsupported forks or modifications
- Denial-of-service attacks without a reproducible exploit

---

## 5. Security Design Principles

Observability One follows these core principles:

- **Least privilege**
- **Defense in depth**
- **Secure by default**
- **Fail safely**
- **Explicit trust boundaries**

---

## 6. Secrets & Credentials

- Secrets must **never** be committed to the repository
- API keys and credentials must be provided via environment variables or
  secret managers
- `.env` files are excluded via `.gitignore`
- CI secrets are stored using GitHub Actions secrets

---

## 7. Data Handling & Privacy

- Telemetry data is treated as sensitive by default
- No telemetry is persisted unless explicitly configured
- PII should be scrubbed or hashed before ingestion
- RCA logic operates on metadata and aggregates where possible

---

## 8. Dependency & Supply Chain Security

- Dependencies are scanned regularly for vulnerabilities
- CI includes dependency and container security scanning
- Lockfiles are recommended
- Minimal base images are preferred for containers

---

## 9. Secure Development Practices

Contributors are expected to:
- Validate all external inputs
- Avoid unsafe deserialization
- Use secure defaults
- Log security-relevant events
- Write deterministic, auditable logic

Security reviews may be required for sensitive changes.

---

## 10. Incident Response

If a security issue is confirmed:
1. Impact is assessed
2. A fix is developed and tested
3. A security advisory is published
4. Users are notified if necessary

---

## 11. Acknowledgements

We appreciate responsible security research and will acknowledge contributors
who report valid security issues, where appropriate.

---

## 12. Final Note

Security is an ongoing process.

Observability One prioritizes **transparency, accountability, and safety**
while enabling deep system insight.

Thank you for helping keep the platform secure.
