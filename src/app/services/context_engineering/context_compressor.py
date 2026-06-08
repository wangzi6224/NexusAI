from src.app.services.context_engineering.schemas import (
    ContextItem,
    CompressedContextItem,
)
from src.app.services.context_engineering.token_estimator import TokenEstimator


class ContextCompressor:
    def __init__(self, estimator: TokenEstimator | None = None) -> None:
        self.estimator = estimator or TokenEstimator()

    def compress_to_budget(
        self,
        item: ContextItem,
        max_tokens: int,
    ) -> CompressedContextItem | None:
        """
        TODO: 当前只实现了 head_tail 方法的压缩，后续可以增加其他方法，如直接截断（truncate）或用 LLM 生成摘要（llm_summary）。 --- IGNORE ---
        """
        if not item.compressible:
            return None

        if item.estimated_tokens <= max_tokens:
            return None

        content = item.content
        max_chars = max(
            200, int(len(content) * max_tokens / max(item.estimated_tokens, 1))
        )

        if max_chars >= len(content):
            return None

        head_chars = int(max_chars * 0.7)
        tail_chars = max_chars - head_chars

        compressed_content = (
            content[:head_chars]
            + "\n\n...[中间内容因上下文预算被压缩]...\n\n"
            + content[-tail_chars:]
        )

        compressed_item = item.model_copy(
            update={
                "content": compressed_content,
                "estimated_tokens": self.estimator.estimate(compressed_content),
                "metadata": {
                    **item.metadata,
                    "compressed": True,
                    "compression_method": "head_tail",
                },
            }
        )

        return CompressedContextItem(
            original_item_id=item.id,
            compressed_item=compressed_item,
            original_tokens=item.estimated_tokens,
            compressed_tokens=compressed_item.estimated_tokens,
            method="head_tail",
        )
