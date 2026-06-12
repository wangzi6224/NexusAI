from __future__ import annotations

from src.app.config import get_settings
from src.app.services.observability.trace_schema import TraceSpan


class LangfuseAdapter:
    """Langfuse 适配器。

    第一版默认 no-op。
    只有配置 LANGFUSE_ENABLED=true 时才实际发送。
    """

    def enabled(self) -> bool:
        return bool(getattr(get_settings(), "langfuse_enabled", False))

    def export_span(self, span: TraceSpan) -> None:
        if not self.enabled():
            return

        # Week 20 先预留接口，不强引入 langfuse SDK。
        # 后续接入时把 TraceSpan 映射为 Langfuse trace / span / generation。
        return
