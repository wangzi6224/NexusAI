import sys


def get_user_input() -> str:
    if len(sys.argv) > 1:
        return " ".join(sys.argv[1:]).strip()

    return input("请输入你的问题：").strip()