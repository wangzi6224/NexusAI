# src/app/services/context_engineering/context_auditor.py
from src.app.services.context_engineering.schemas import ContextItem


class ContextAuditor:
    """上下文审计器。

    负责对上下文项进行安全审计，标记潜在的注入风险。
    """

    INJECTION_PATTERNS = [
        "忽略以上规则",
        "忽略之前的指令",
        "ignore previous instructions",
        "system prompt",
        "泄露密钥",
        "api_key",
        "delete_database",
        "执行命令",
    ]

    def audit_item(self, item: ContextItem) -> ContextItem:
        content_lower = item.content.lower()
        matched = [
            pattern
            for pattern in self.INJECTION_PATTERNS
            if pattern.lower() in content_lower
        ]

        if not matched:
            return item

        return item.model_copy(
            update={
                "metadata": {
                    **item.metadata,
                    "injection_risk": True,
                    "matched_patterns": matched,
                }
            }
        )
