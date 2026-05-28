import logging

from src.app.config import get_log_level
from src.app.paths import LOG_DIR


def get_logger() -> logging.Logger:
    logger = logging.getLogger("NexusAI")

    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, get_log_level().upper(), logging.INFO))

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    file_handler = logging.FileHandler(LOG_DIR / "app.log", encoding="utf-8")
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
