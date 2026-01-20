"""
Base Exporter Interface

Defines the contract for all telemetry exporters in Observability One.
All vendor-specific exporters (Datadog, CloudWatch, Splunk, SigNoz, etc.)
must inherit from this base class.

Design goals:
- Vendor-agnostic
- Fault-tolerant
- Observable (metrics + logs)
- Safe (no data loss on partial failures)
"""

from abc import ABC, abstractmethod
from typing import Iterable, Dict, Any
import logging
import time

logger = logging.getLogger(__name__)


class ExportResult:
    """
    Standardized exporter result object.
    """
    def __init__(
        self,
        success: bool,
        exported_count: int = 0,
        failed_count: int = 0,
        error: str | None = None,
        latency_ms: float | None = None,
    ):
        self.success = success
        self.exported_count = exported_count
        self.failed_count = failed_count
        self.error = error
        self.latency_ms = latency_ms

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "exported_count": self.exported_count,
            "failed_count": self.failed_count,
            "error": self.error,
            "latency_ms": self.latency_ms,
        }


class BaseExporter(ABC):
    """
    Abstract base class for all exporters.

    Exporters are responsible for translating canonical telemetry
    (logs, metrics, traces) into vendor-specific formats and delivering
    them reliably to external systems.
    """

    def __init__(self, name: str, enabled: bool = True):
        self.name = name
        self.enabled = enabled

    # ---------------------------
    # Public API
    # ---------------------------

    def export(self, records: Iterable[Dict[str, Any]]) -> ExportResult:
        """
        Entry point for exporting telemetry.

        Handles:
        - enable/disable logic
        - timing
        - error isolation
        - standardized result reporting
        """

        if not self.enabled:
            logger.info("Exporter '%s' is disabled", self.name)
            return ExportResult(success=True, exported_count=0)

        start = time.time()

        try:
            exported, failed = self._export(records)
            latency_ms = (time.time() - start) * 1000

            logger.info(
                "Exporter '%s' completed | exported=%d failed=%d latency_ms=%.2f",
                self.name,
                exported,
                failed,
                latency_ms,
            )

            return ExportResult(
                success=True,
                exported_count=exported,
                failed_count=failed,
                latency_ms=latency_ms,
            )

        except Exception as exc:
            latency_ms = (time.time() - start) * 1000
            logger.exception("Exporter '%s' failed", self.name)

            return ExportResult(
                success=False,
                exported_count=0,
                failed_count=len(list(records)),
                error=str(exc),
                latency_ms=latency_ms,
            )

    # ---------------------------
    # Required Implementations
    # ---------------------------

    @abstractmethod
    def _export(self, records: Iterable[Dict[str, Any]]) -> tuple[int, int]:
        """
        Perform the actual export.

        Must return:
        (exported_count, failed_count)

        This method should:
        - Be idempotent where possible
        - Fail fast on configuration errors
        - Continue on partial failures
        """
        raise NotImplementedError

    # ---------------------------
    # Optional Hooks
    # ---------------------------

    def health_check(self) -> bool:
        """
        Verify exporter connectivity and credentials.

        Called during startup and periodically by the platform.
        """
        return True

    def shutdown(self) -> None:
        """
        Graceful shutdown hook.
        """
        logger.info("Shutting down exporter '%s'", self.name)

    # ---------------------------
    # Utility Helpers
    # ---------------------------

    def _chunk(self, records: Iterable[Dict[str, Any]], size: int = 500):
        """
        Yield records in chunks to avoid payload limits.
        """
        batch = []
        for record in records:
            batch.append(record)
            if len(batch) >= size:
                yield batch
                batch = []
        if batch:
            yield batch
