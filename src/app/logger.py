import logging
from pathlib import Path

from src.app.config import get_log_level


def get_logger() -> logging.Logger:
    logger = logging.getLogger("my_python_project")

    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, get_log_level().upper(), logging.INFO))

    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    file_handler = logging.FileHandler(log_dir / "app.log", encoding="utf-8")
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger