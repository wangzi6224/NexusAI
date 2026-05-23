from src.app.services.agent.state import AgentState


class AgentPromptBuilder:
    def build_final_messages(self, state: AgentState) -> list[dict[str, str]]:
        tool_results = []

        for step in state.steps:
            if step.type == "tool_call":
                tool_results.append(
                    {
                        "tool_name": step.tool_name,
                        "arguments": step.arguments,
                        "result": step.result,
                    }
                )

        system_prompt = """
你是一个企业知识库 AI Agent。

你需要根据【工具调用结果】回答用户问题。

严格要求：
1. 优先依据工具结果回答。
2. 如果工具结果没有足够依据，请明确说明“根据当前知识库资料，无法确定”。
3. 不要编造工具结果里不存在的规范、接口、文件名。
4. 如果是代码或组件模板问题，请给出清晰示例。
5. 使用简体中文。
6. 回答要结构化。
""".strip()

        user_prompt = f"""
【用户问题】
{state.question}

【工具调用结果】
{tool_results}

请生成最终回答：
""".strip()

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
