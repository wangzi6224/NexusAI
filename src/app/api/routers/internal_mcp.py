from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from src.app.services.mcp.auth import verify_mcp_token
from src.app.services.tools.list_docs import ListDocsTool
from src.app.services.tools.search_docs import SearchDocsTool
from src.app.services.tools.read_doc import ReadDocTool

router = APIRouter(prefix="/internal/mcp/tools", tags=["internal-mcp"])


@router.post("/list-docs", dependencies=[Depends(verify_mcp_token)])
def mcp_list_docs(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    return ListDocsTool().run(payload or {})


@router.post("/search-docs", dependencies=[Depends(verify_mcp_token)])
def mcp_search_docs(payload: dict[str, Any]) -> dict[str, Any]:
    return SearchDocsTool().run(payload)


@router.post("/read-doc", dependencies=[Depends(verify_mcp_token)])
def mcp_read_doc(payload: dict[str, Any]) -> dict[str, Any]:
    return ReadDocTool().run(payload)
