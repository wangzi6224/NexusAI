from typing import Any


class RagPromptBuilder:
    def build(
        self,
        question: str,
        chunks: list[dict[str, Any]],
    ) -> list[dict[str, str]]:
        context = self._build_context(chunks)

        system_prompt = """
你是一个企业知识库问答助手。

你必须严格根据【资料】回答用户问题。

规则：
1. 如果资料中有明确答案，请基于资料回答。
2. 如果资料中没有明确答案，请回答：“根据当前知识库资料，无法确定。”
3. 不要编造资料中不存在的内容。
4. 回答要简洁、准确、结构清晰。
5. 如果涉及代码规范或技术方案，尽量给出示例。
6. 使用简体中文。
""".strip()

        user_prompt = f"""
【资料】
{context}

【用户问题】
{question}
""".strip()

        return [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ]

    def _build_context(self, chunks: list[dict[str, Any]]) -> str:
        if not chunks:
            return "无可用资料。"

        parts: list[str] = []

        for index, chunk in enumerate(chunks, start=1):
            filename = chunk.get("filename") or "未知文档"
            heading = chunk.get("heading") or "无标题"
            content = chunk.get("content") or ""

            parts.append(f"""
[资料 {index}]
文档：{filename}
标题：{heading}
Chunk ID：{chunk["chunk_id"]}
相关分数：{chunk["score"]}

内容：
{content}
""".strip())

        return "\n\n---\n\n".join(parts)
