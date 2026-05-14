import os
import signal
import uvicorn
import subprocess
import time
from src.app.paths import WEB_DIR


def start_web_server() -> None:
    print("正在启动前端开发服务器...")
    print(f"前端目录: {WEB_DIR}")
    subprocess.Popen(["pnpm", "run", "dev"], cwd=WEB_DIR)


def _find_listening_pids(port: int) -> list[int]:
    result = subprocess.run(
        ["lsof", "-ti", f"tcp:{port}", "-sTCP:LISTEN"],
        capture_output=True,
        text=True,
        check=False,
    )
    pids: list[int] = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if line.isdigit():
            pids.append(int(line))
    return pids


def _get_process_cmdline(pid: int) -> str:
    result = subprocess.run(
        ["ps", "-p", str(pid), "-o", "command="],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip()


def _is_our_backend_process(cmdline: str) -> bool:
    return (
        "src.app.main" in cmdline
        or "src.app.server:app" in cmdline
        or "uvicorn" in cmdline
        and "my_python_project" in cmdline
    )


def ensure_backend_port_available(port: int) -> None:
    pids = _find_listening_pids(port)
    if not pids:
        return

    terminated = []
    for pid in pids:
        cmdline = _get_process_cmdline(pid)
        if not cmdline:
            continue
        if _is_our_backend_process(cmdline):
            try:
                os.kill(pid, signal.SIGTERM)
                terminated.append(pid)
            except ProcessLookupError:
                continue

    if terminated:
        print(f"检测到端口 {port} 被旧后端进程占用，已尝试清理: {terminated}")
        deadline = time.time() + 3
        while time.time() < deadline:
            if not _find_listening_pids(port):
                return
            time.sleep(0.1)

    remain = _find_listening_pids(port)
    if remain:
        raise RuntimeError(
            f"端口 {port} 仍被占用（PID: {remain}）。请先释放端口，或改用其他端口启动。"
        )


def main() -> None:
    ensure_backend_port_available(8000)
    start_web_server()
    uvicorn.run(
        "src.app.server:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    main()
