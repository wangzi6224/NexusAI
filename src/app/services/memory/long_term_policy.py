from __future__ import annotations

import re

from src.app.services.memory.long_term_schemas import ExtractedLongTermMemoryCandidate

# 显式记忆请求的正则模式，用于判断用户是否明确要求将内容保存为长期记忆
EXPLICIT_MEMORY_PATTERNS = [
    r"记住",
    r"帮我记一下",
    r"以后.*默认",
    r"从现在开始",
    r"以后回答.*用",
    r"后续.*都",
    r"以后.*优先",
]

SENSITIVE_HINTS = [
    "身份证",
    "银行卡",
    "密码",
    "token",
    "api key",
    "apikey",
    "私钥",
    "secret",
    "access key",
]


class LongTermMemoryPolicy:
    """长期记忆策略：决定何时将候选记忆保存到存储中。"""

    def is_explicit_memory_request(self, text: str) -> bool:
        """判断用户是否发出了显式的“记住我”类请求。"""
        return any(
            re.search(pattern, text, re.IGNORECASE)
            for pattern in EXPLICIT_MEMORY_PATTERNS
        )

    def should_store_candidate(
        self,
        candidate: ExtractedLongTermMemoryCandidate,
    ) -> tuple[bool, str]:
        """决定候选记忆是否应当保存。

        返回 (是否保存, 原因代码)。
        """
        content = candidate.content.strip()

        # 内容太短，一般不适合作为长期记忆
        if len(content) < 6:
            return False, "content_too_short"

        # 置信度不足，可能不是重要记忆
        if candidate.confidence < 0.55:
            return False, "low_confidence"

        # 重要性低，不必保存为长期记忆
        if candidate.importance < 0.35:
            return False, "low_importance"

        # 避免保存敏感信息
        if self._looks_sensitive(content):
            return False, "sensitive_content"

        # 避免保存临时性、短期信息
        if self._looks_temporary(content):
            return False, "temporary_content"

        return True, "accepted"

    def _looks_sensitive(self, content: str) -> bool:
        """判断内容是否包含敏感信息提示。"""
        lower = content.lower()
        return any(hint in lower for hint in SENSITIVE_HINTS)

    def _looks_temporary(self, content: str) -> bool:
        """判断内容是否属于临时性信息，不适合集成到长期记忆。"""
        temporary_keywords = [
            "今天",
            "明天",
            "刚才",
            "这一次",
            "临时",
            "等会",
            "马上",
        ]
        return any(keyword in content for keyword in temporary_keywords)
