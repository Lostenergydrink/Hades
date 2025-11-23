from __future__ import annotations

import logging
from threading import Lock

try:  # pragma: no cover - optional dependency guard
    from agent_framework.observability import setup_observability
except Exception:  # pragma: no cover - agent framework may be unavailable during tests
    setup_observability = None  # type: ignore[assignment]

_LOGGER = logging.getLogger(__name__)
_CONFIGURED = False
_LOCK = Lock()


def ensure_tracing(otlp_endpoint: str = "http://localhost:4317") -> None:
    """Idempotently wires up Agent Framework tracing via OpenTelemetry."""

    global _CONFIGURED
    if _CONFIGURED:
        return
    with _LOCK:
        if _CONFIGURED:
            return
        if setup_observability is None:
            _LOGGER.debug("agent-framework tracing unavailable; setup_observability import failed")
            _CONFIGURED = True  # avoid repeated logs even if missing
            return
        setup_observability(
            otlp_endpoint=otlp_endpoint,
            enable_sensitive_data=True,
        )
        _LOGGER.info("Agent Framework tracing enabled via %s", otlp_endpoint)
        _CONFIGURED = True
