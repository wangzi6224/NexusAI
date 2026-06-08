from src.app.services.context_engineering.schemas import ContextItem


class ContextRanker:
    """上下文排序器。

    第一版使用确定性规则，不依赖 LLM。
    这样可测试、可解释、可复现。
    """

    def rank(self, items: list[ContextItem]) -> list[ContextItem]:
        return sorted(
            items,
            key=lambda item: self._score(item),
            reverse=True,
        )

    def _score(self, item: ContextItem) -> float:
        """计算 ContextItem 综合得分。

        当前采用确定性规则排序，避免依赖 LLM，
        保证结果可测试、可解释、可复现。

        评分公式：

            final_score =
                priority * 0.6
                + score * 40
                + placement_bonus
                + required_bonus

        各字段含义：

        - priority
            人工定义的重要等级，通常范围 0~100。
            用于体现上下文类型的重要性：
            system > safety > memory > source > message。

        - score
            内容相关性评分，范围 0~1。
            通常来自：
            - Memory 相似度
            - RAG Rerank 分数
            - Graph 检索分数
            - Tool Observation 相关度

        - placement_bonus
            placement == "system" 时额外 +5 分，
            保证系统提示词和安全策略优先保留。

        - required_bonus
            required == True 时额外 +10 分，
            保证关键上下文不会因 Token Budget 被丢弃。

        理论得分范围：

            最低分：
                0 * 0.6 + 0 * 40 + 0 + 0
                = 0

            最高分：
                100 * 0.6 + 1 * 40 + 5 + 10
                = 115

        实际业务中常见范围：

            20 ~ 90

        得分越高，越优先进入最终 Context Package，
        后续 ContextBudget 会优先保留高分项，
        低分项可能被压缩或丢弃。

        Args:
            item: 待排序的上下文项

        Returns:
            综合排序得分
        """
        placement_bonus = 5 if item.placement == "system" else 0
        required_bonus = 10 if item.required else 0
        return item.priority * 0.6 + item.score * 40 + placement_bonus + required_bonus
