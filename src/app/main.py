import uvicorn
import subprocess
from src.app.paths import WEB_DIR


def start_web_server() -> None:
    print("正在启动前端开发服务器...")
    print(f"前端目录: {WEB_DIR}")
    subprocess.Popen(["pnpm", "run", "dev"], cwd=WEB_DIR)


def main() -> None:
    start_web_server()
    uvicorn.run(
        "src.app.server:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    main()
