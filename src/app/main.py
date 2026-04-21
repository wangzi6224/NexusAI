from datetime import datetime
from time import perf_counter

from src.app.cli import get_user_input
from src.app.client import chat_completion
from src.app.health import check_ollama_model_exists, check_ollama_server
from src.app.history import append_history
from src.app.logger import get_logger
from src.app.prompts import build_chat_prompt
from src.app.config import get_ollama_model


def main() -> None:
    logger = get_logger()

    ok, message = check_ollama_server()
    if not ok:
        print(message)
        logger.error(message)
        return

    logger.info(message)

    ok, message = check_ollama_model_exists()
    if not ok:
        print(message)
        logger.error(message)
        return

    logger.info(message)

    user_input = get_user_input()
    if not user_input:
        print("输入不能为空")
        logger.warning("用户输入为空")
        return

    prompt = build_chat_prompt(user_input)

    logger.info("开始请求模型，model=%s", get_ollama_model())

    start = perf_counter()
    try:
        answer = chat_completion(prompt)
    except Exception as exc:
        logger.exception("调用模型失败: %s", exc)
        print(f"\n调用失败：{exc}")
        return
    elapsed = perf_counter() - start

    logger.info("模型调用成功，耗时 %.2f 秒", elapsed)

    append_history(
        {
            "timestamp": datetime.now().isoformat(),
            "model": get_ollama_model(),
            "user_input": user_input,
            "prompt": prompt,
            "answer": answer,
            "elapsed_seconds": round(elapsed, 2),
        }
    )

    print("\n模型回答：")
    print(answer)


if __name__ == "__main__":
    main()