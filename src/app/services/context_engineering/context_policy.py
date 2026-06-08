from src.app.services.context_engineering.schemas import ContextItem


class ContextPolicy:
    EXTERNAL_TYPES = {
        "long_term_memory",
        "retrieved_source",
        "read_document",
        "tool_observation",
        "working_memory",
    }

    def normalize(self, item: ContextItem) -> ContextItem:
        """修正不安全 placement。

        外部资料即使被错误创建成 system，也强制降级到 user_data。
        """

        if item.type in self.EXTERNAL_TYPES and item.placement == "system":
            return item.model_copy(
                update={
                    "placement": "user_data",
                    "metadata": {
                        **item.metadata,
                        "policy_adjusted": True,
                        "policy_reason": "external_context_must_not_be_system",
                    },
                }
            )
        return item
