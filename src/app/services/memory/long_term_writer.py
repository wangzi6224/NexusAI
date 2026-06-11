from __future__ import annotations

import json
from time import perf_counter
from typing import Any

from pydantic import TypeAdapter, ValidationError

from src.app.services.llm.factory import get_llm_provider
from src.app.services.memory.long_term_deduper import LongTermMemoryDeduper
from src.app.services.memory.long_term_policy import LongTermMemoryPolicy
from src.app.services.memory.long_term_schemas import (
    ExtractedLongTermMemoryCandidate,
    LongTermMemoryCreate,
    LongTermMemoryWriteResult,
)
from src.app.services.memory.long_term_store import LongTermMemoryStore
from src.app.services.memory.memory_prompt import (
    LONG_TERM_MEMORY_EXTRACTOR_PROMPT_VERSION,
    LONG_TERM_MEMORY_EXTRACTOR_SYSTEM_PROMPT,
)

CandidateListAdapter = TypeAdapter(list[ExtractedLongTermMemoryCandidate])


class LongTermMemoryWriter:
    def __init__(self) -> None:
        self.llm_provider = get_llm_provider()
        self.store = LongTermMemoryStore()
        self.policy = LongTermMemoryPolicy()
        self.deduper = LongTermMemoryDeduper(self.store)

    def write_from_turn(
        self,
        *,
        user_message: str,
        assistant_answer: str,
        user_id: str = "default_user",
        workspace_id: str | None = None,
        conversation_id: str | None = None,
        source_message_id: str | None = None,
        source_run_id: str | None = None,
        model: str | None = None,
    ) -> LongTermMemoryWriteResult:
        start = perf_counter()

        candidates = self._extract_candidates(
            user_message=user_message,
            assistant_answer=assistant_answer,
            model=model,
        )

        created = []
        skipped: list[dict[str, Any]] = []

        for candidate in candidates:
            accepted, reason = self.policy.should_store_candidate(candidate)

            if not accepted:
                # 该候选记忆不符合存储策略，不予存储，并记录原因
                skipped.append(
                    {
                        "content": candidate.content,
                        "reason": reason,
                        "candidate": candidate.model_dump(mode="json"),
                    }
                )
                continue

            # 构建 LongTermMemoryCreate 对象，准备存储
            payload = LongTermMemoryCreate(
                user_id=user_id,
                workspace_id=workspace_id,
                conversation_id=conversation_id,
                source_message_id=source_message_id,
                source_run_id=source_run_id,
                memory_type=candidate.memory_type,
                content=candidate.content,
                importance=candidate.importance,
                confidence=candidate.confidence,
                metadata={
                    "source": candidate.source,
                    "extract_reason": candidate.reason,
                    "extractor": "llm",
                    "prompt_version": LONG_TERM_MEMORY_EXTRACTOR_PROMPT_VERSION,
                },
            )

            duplicate = self.deduper.find_duplicate(payload)
            if duplicate is not None:
                # 判断是否与现有记忆相似到可以覆盖的程度，如果是，则更新现有记忆；
                skipped.append(
                    {
                        "content": candidate.content,
                        "reason": "duplicate_or_similar_memory",
                        "existing_memory_id": duplicate.id,
                    }
                )
                continue

            created.append(self.store.create(payload))

        latency_ms = int((perf_counter() - start) * 1000)

        return LongTermMemoryWriteResult(
            created=created,
            skipped=skipped,
            trace={
                "prompt_version": LONG_TERM_MEMORY_EXTRACTOR_PROMPT_VERSION,
                "candidate_count": len(candidates),
                "created_count": len(created),
                "skipped_count": len(skipped),
                "latency_ms": latency_ms,
            },
        )

    def _extract_candidates(
        self,
        *,
        user_message: str,
        assistant_answer: str,
        model: str | None,
    ) -> list[ExtractedLongTermMemoryCandidate]:
        messages = [
            {
                "role": "system",
                "content": LONG_TERM_MEMORY_EXTRACTOR_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": (
                    "请从下面这一轮对话中提取长期记忆。\n\n"
                    f"用户输入：\n{user_message}\n\n"
                    f"助手回答：\n{assistant_answer}\n"
                ),
            },
        ]

        response = self.llm_provider.chat(
            messages=messages,
            model=model,
            thinking_enabled=False,
        )

        try:
            payload = self._parse_json_array(response.content)
            return CandidateListAdapter.validate_python(payload)
        except (json.JSONDecodeError, ValidationError, TypeError, ValueError):
            return []

    def _parse_json_array(self, content: str) -> Any:
        clean = content.strip()

        if clean.startswith("```"):
            clean = clean.strip("`")
            clean = clean.removeprefix("json").strip()

        return json.loads(clean)
