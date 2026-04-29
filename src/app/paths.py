from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
LOG_DIR = Path.cwd() / "logs"
DATA_DIR = Path.cwd() / "data"
WEB_DIR = BASE_DIR.parent.parent / "web"
