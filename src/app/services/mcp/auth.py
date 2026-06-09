# src/app/services/mcp/auth.py
from __future__ import annotations

from fastapi import Header, HTTPException

from src.app.config import get_settings


def verify_mcp_token(authorization: str | None = Header(default=None)) -> None:
    expected = getattr(get_settings(), "nexusai_mcp_token", "")
    if not expected:
        raise HTTPException(status_code=503, detail="MCP token 未配置")

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="缺少 MCP token")

    token = authorization.removeprefix("Bearer ").strip()
    if token != expected:
        raise HTTPException(status_code=403, detail="MCP token 无效")
