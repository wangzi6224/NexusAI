from __future__ import annotations

from json import dumps
from typing import Any


def sse_event(event: str, data: Any) -> str:
    """构造标准 SSE 字符串。"""

    if isinstance(data, str):
        payload = data
    else:
        payload = dumps(data, ensure_ascii=False)

    return f"event: {event}\ndata: {payload}\n\n"
