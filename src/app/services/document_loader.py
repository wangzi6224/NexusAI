import re
import uuid
from pathlib import Path

from src.app.exceptions import AppError
from src.app.paths import UPLOAD_DIR

ALLOWED_DOCUMENT_EXTENSIONS = {".md", ".txt"}
MAX_DOCUMENT_FILE_SIZE_BYTES = 5 * 1024 * 1024


class DocumentLoader:
    def validate_file(self, filename: str, content: bytes) -> str:
        if not filename:
            raise AppError(
                code="DOCUMENT_INVALID_FILE",
                message="文件名不能为空",
                status_code=400,
            )

        suffix = Path(filename).suffix.lower()

        if suffix not in ALLOWED_DOCUMENT_EXTENSIONS:
            raise AppError(
                code="DOCUMENT_UNSUPPORTED_FILE_TYPE",
                message="暂只支持 .md 和 .txt 文件",
                detail=f"filename={filename}",
                status_code=400,
            )

        if not content:
            raise AppError(
                code="DOCUMENT_EMPTY_FILE",
                message="上传文件不能为空",
                status_code=400,
            )

        if len(content) > MAX_DOCUMENT_FILE_SIZE_BYTES:
            raise AppError(
                code="DOCUMENT_FILE_TOO_LARGE",
                message="上传文件过大",
                detail=f"max_size_bytes={MAX_DOCUMENT_FILE_SIZE_BYTES}",
                status_code=400,
            )

        return suffix.lstrip(".")

    def save_upload_file(self, filename: str, content: bytes) -> Path:
        try:
            UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

            safe_name: str = self._safe_filename(filename)
            saved_name: str = f"{uuid.uuid4()}_{safe_name}"
            saved_path: Path = UPLOAD_DIR / saved_name

            saved_path.write_bytes(content)

            return saved_path
        except PermissionError as exc:
            raise AppError(
                code="DOCUMENT_SAVE_PERMISSION_ERROR",
                message="保存上传文件时权限不足",
                detail=str(exc),
                status_code=500,
            ) from exc
        except OSError as exc:
            raise AppError(
                code="DOCUMENT_SAVE_ERROR",
                message="保存上传文件时发生错误",
                detail=str(exc),
                status_code=500,
            ) from exc

    def load_text(self, filename: str, content: bytes) -> str:
        self.validate_file(filename=filename, content=content)

        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise AppError(
                code="DOCUMENT_DECODE_ERROR",
                message="文件文本解码失败，请确认文件是 UTF-8 编码",
                detail=str(exc),
                status_code=400,
            ) from exc

        text = text.strip()

        if not text:
            raise AppError(
                code="DOCUMENT_EMPTY_TEXT",
                message="文件解析后文本为空",
                status_code=400,
            )

        return text

    def _safe_filename(self, filename: str) -> str:
        name = Path(filename).name
        return re.sub(r"[^a-zA-Z0-9._\-\u4e00-\u9fff]", "_", name)
