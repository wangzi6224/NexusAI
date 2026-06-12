from __future__ import annotations

from src.app.config import get_settings
from src.app.services.observability.trace_schema import TraceSpan


class OpenTelemetryAdapter:
    """OpenTelemetry 适配器。

    第一版只预留映射层，不强依赖 otel SDK。
    """

    def enabled(self) -> bool:
        return bool(getattr(get_settings(), "otel_enabled", False))

    def export_span(self, span: TraceSpan) -> None:
        if not self.enabled():
            return

        # 后续可以把 TraceSpan 映射成 OTel span:
        # span_type -> span name
        # metadata -> attributes
        # status -> status code
        return
