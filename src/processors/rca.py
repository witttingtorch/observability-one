"""
Root Cause Analysis (RCA) Engine

Consumes correlation groups and produces ranked, explainable
root cause candidates.

Design goals:
- Deterministic and explainable scoring
- Evidence-driven output
- Configurable weighting
- Safe for audits and postmortems
"""

from dataclasses import dataclass
from typing import List, Dict, Any
import time


# ============================
# Data Models
# ============================

@dataclass
class RootCause:
    """
    Represents a ranked root cause candidate.
    """
    service: str
    description: str
    confidence_score: float
    severity_score: float
    correlation_score: float
    impacted_services: List[str]
    signals: List[Dict[str, Any]]
    start_time: float
    end_time: float
    explanation: str


# ============================
# RCA Engine
# ============================

class RCAEngine:
    """
    Converts correlated signal groups into ranked root causes.
    """

    def __init__(
        self,
        weight_severity: float = 0.4,
        weight_correlation: float = 0.4,
        weight_blast_radius: float = 0.2,
    ):
        self.weight_severity = weight_severity
        self.weight_correlation = weight_correlation
        self.weight_blast_radius = weight_blast_radius

    # ----------------------------
    # Public API
    # ----------------------------

    def analyze(self, correlation_groups) -> List[RootCause]:
        """
        Produce ranked root causes from correlation groups.
        """
        causes: List[RootCause] = []

        for group in correlation_groups:
            rc = self._build_root_cause(group)
            causes.append(rc)

        causes.sort(key=lambda c: c.confidence_score, reverse=True)
        return causes

    # ----------------------------
    # Core Logic
    # ----------------------------

    def _build_root_cause(self, group) -> RootCause:
        impacted_services = sorted({s.service for s in group.signals})

        severity = self._calculate_severity(group)
        blast_radius = len(impacted_services)
        correlation = group.correlation_score

        confidence = self._calculate_confidence(
            severity, correlation, blast_radius
        )

        description = (
            f"Probable issue detected in {group.primary_service} "
            f"impacting {len(impacted_services)} service(s)."
        )

        explanation = (
            f"Root cause analysis identified correlated signals "
            f"across services {', '.join(impacted_services)} "
            f"between {self._fmt(group.start_time)} and "
            f"{self._fmt(group.end_time)}. "
            f"Correlation strength={correlation:.2f}, "
            f"blast radius={blast_radius}."
        )

        return RootCause(
            service=group.primary_service,
            description=description,
            confidence_score=round(confidence, 2),
            severity_score=round(severity, 2),
            correlation_score=round(correlation, 2),
            impacted_services=impacted_services,
            signals=[s.payload for s in group.signals],
            start_time=group.start_time,
            end_time=group.end_time,
            explanation=explanation,
        )

    # ----------------------------
    # Scoring
    # ----------------------------

    def _calculate_severity(self, group) -> float:
        """
        Estimate severity from anomaly signals.
        """
        severities = []

        for s in group.signals:
            if s.signal_type == "anomaly":
                sev = s.payload.get("severity")
                if sev is not None:
                    severities.append(sev)

        if not severities:
            return 1.0

        return max(severities)

    def _calculate_confidence(
        self, severity: float, correlation: float, blast_radius: int
    ) -> float:
        """
        Weighted confidence score (0–100).
        """
        norm_severity = min(severity / 10.0, 1.0)
        norm_correlation = min(correlation / 10.0, 1.0)
        norm_blast = min(blast_radius / 10.0, 1.0)

        score = (
            norm_severity * self.weight_severity
            + norm_correlation * self.weight_correlation
            + norm_blast * self.weight_blast_radius
        )

        return score * 100.0

    # ----------------------------
    # Helpers
    # ----------------------------

    def _fmt(self, ts: float) -> str:
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))


# ============================
# Example Usage
# ============================

if __name__ == "__main__":
    # Example assumes CorrelationGroup-like objects
    from types import SimpleNamespace

    now = time.time()
    group = SimpleNamespace(
        primary_service="checkout",
        start_time=now - 120,
        end_time=now,
        correlation_score=7.5,
        signals=[
            SimpleNamespace(
                signal_type="anomaly",
                service="checkout",
                timestamp=now - 60,
                payload={"severity": 8.5},
            ),
            SimpleNamespace(
                signal_type="log",
                service="payment",
                timestamp=now - 50,
                payload={"message": "timeout"},
            ),
        ],
    )

    engine = RCAEngine()
    results = engine.analyze([group])

    for r in results:
        print(r)
