from __future__ import annotations

from typing import TYPE_CHECKING, Sequence

from src.app.config import Settings, get_settings

if TYPE_CHECKING:
    from FlagEmbedding import FlagReranker


class BgeRerankerProvider:
    """
    BGE Reranker 模型调用层。

    这个类只负责一件事：
    输入 query + passages，输出每个 passage 的相关性分数。

    它不负责：
    - 排序；
    - top_n 截断；
    - trace；
    - fallback；
    - API 入参校验。

    这样做是为了把“模型能力”和“业务编排”拆开。
    """

    def __init__(
        self,
        model_name: str | None = None,
        use_fp16: bool | None = None,
    ) -> None:
        settings: Settings = get_settings()

        # 初始化模型配置
        self.model_name: str = model_name or settings.reranker_model

        # 是否使用 fp16 取决于入参（优先）和全局配置（次优先）。
        self.use_fp16: bool = (
            use_fp16 if use_fp16 is not None else settings.reranker_use_fp16
        )

        # 模型实例，初始为 None，使用时才加载。
        self._model: FlagReranker | None = None

    def _get_model(self) -> FlagReranker:
        """
        延迟加载模型。

        为什么要延迟加载？
        1. 避免服务启动时就加载大模型；
        2. 避免健康检查接口变慢；
        3. 方便测试时 mock；
        4. 方便未来做模型切换。
        """

        if self._model is None:
            from FlagEmbedding import FlagReranker

            self._model = FlagReranker(
                self.model_name,
                use_fp16=self.use_fp16,
            )

        return self._model

    def score(
        self,
        query: str,
        passages: Sequence[str],
    ) -> list[float]:
        """
        计算 query 与多个 passage 的相关性分数。

        参数：
        - query：通常是 rewrite 后的问题；
        - passages：候选 chunk 的 content 列表。

        返回：
        - 每个 passage 对应一个 float 分数；
        - 分数越高，表示越相关。
        """

        if not passages:
            return []

        pairs: list[tuple[str, str]] = [(query, passage) for passage in passages]
        raw_scores: list[float] = self._get_model().compute_score(pairs)

        return [float(score) for score in raw_scores]
