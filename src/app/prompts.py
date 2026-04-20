def build_chat_prompt(user_input: str) -> str:
    return f"""你是一名专业、清晰、准确的 AI 助手。
请用简体中文回答下面的问题，并尽量讲清楚步骤。

用户问题：
{user_input}
"""
