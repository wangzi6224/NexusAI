from src.app.client import chat_completion
from src.app.prompts import build_chat_prompt


def main() -> None:
    user_input = input("请输入你的问题：").strip()

    if not user_input:
        print("输入不能为空")
        return

    prompt = build_chat_prompt(user_input)

    try:
        answer = chat_completion(prompt)
    except Exception as exc:
        print(f"\n调用失败：{exc}")
        return

    print("\n模型回答：")
    print(answer)


if __name__ == "__main__":
    main()