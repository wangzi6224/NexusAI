from pathlib import Path

# 根目录绝对路径
BASE_ABS_DIR = Path(__file__).resolve().parent

# 静态文件目录
STATIC_DIR = BASE_ABS_DIR / "static"

# 日志目录
LOG_DIR = BASE_ABS_DIR / "logs"

# 数据目录
DATA_DIR = BASE_ABS_DIR / "data"

# Web目录
WEB_DIR = BASE_ABS_DIR.parents[1] / "web"

# 上传文件目录
UPLOAD_DIR = DATA_DIR / "uploads"

# 处理后的文件目录
DOCUMENTS_FILE = DATA_DIR / "documents.json"

# 文档分块目录
DOCUMENT_CHUNKS_FILE = DATA_DIR / "document_chunks.json"
