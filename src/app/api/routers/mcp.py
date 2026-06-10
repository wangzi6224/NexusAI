from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query

from src.app.services.mcp.client import McpClient
from src.app.services.mcp.store import McpStore
from src.app.services.mcp.schemas import (
    McpServerCreate,
    McpServerUpdate,
    McpToolCallRequest,
    McpToolCreate,
    McpToolUpdate,
)

router = APIRouter(prefix="/mcp", tags=["mcp"])


@router.get("/servers")
def list_mcp_servers(
    enabled: bool | None = Query(default=None),
) -> dict[str, Any]:
    store = McpStore()
    servers = store.list_servers(enabled=enabled)

    return {
        "items": [item.model_dump(mode="json") for item in servers],
        "count": len(servers),
    }


@router.post("/servers")
def create_mcp_server(payload: McpServerCreate) -> dict[str, Any]:
    store = McpStore()

    try:
        server = store.create_server(payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return server.model_dump(mode="json")


@router.patch("/servers/{server_name}")
def update_mcp_server(
    server_name: str,
    payload: McpServerUpdate,
) -> dict[str, Any]:
    store = McpStore()

    try:
        server = store.update_server(name=server_name, payload=payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return server.model_dump(mode="json")


@router.delete("/servers/{server_name}")
def delete_mcp_server(server_name: str) -> dict[str, Any]:
    store = McpStore()

    try:
        return store.delete_server(server_name)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/tools")
def list_mcp_tools(
    server_name: str | None = None,
    enabled: bool | None = Query(default=None),
) -> dict[str, Any]:
    store = McpStore()
    tools = store.list_tools(server_name=server_name, enabled=enabled)

    return {
        "items": [item.model_dump(mode="json") for item in tools],
        "count": len(tools),
    }


@router.post("/servers/{server_name}/tools")
def create_mcp_tool(
    server_name: str,
    payload: McpToolCreate,
) -> dict[str, Any]:
    store = McpStore()

    try:
        tool = store.create_tool(server_name=server_name, payload=payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return tool.model_dump(mode="json")


@router.patch("/tools/{full_name}")
def update_mcp_tool(
    full_name: str,
    payload: McpToolUpdate,
) -> dict[str, Any]:
    store = McpStore()

    try:
        tool = store.update_tool(full_name=full_name, payload=payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return tool.model_dump(mode="json")


@router.post("/servers/{server_name}/discover")
def discover_mcp_tools(server_name: str) -> dict[str, Any]:
    store = McpStore()
    server = store.get_server(server_name)

    if server is None:
        raise HTTPException(status_code=404, detail=f"MCP Server 不存在: {server_name}")

    try:
        discovered = McpClient().list_tools(server=server)
        saved = store.upsert_discovered_tools(server=server, tools=discovered)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "server_name": server_name,
        "discovered_count": len(discovered),
        "saved_count": len(saved),
        "items": [item.model_dump(mode="json") for item in saved],
    }


@router.post("/tools/{full_name}/call")
def call_mcp_tool(
    full_name: str,
    payload: McpToolCallRequest,
) -> dict[str, Any]:
    store = McpStore()
    tool = store.get_tool(full_name)

    if tool is None:
        raise HTTPException(status_code=404, detail=f"MCP Tool 不存在: {full_name}")

    server = store.get_server(tool.server_name)

    if server is None:
        raise HTTPException(
            status_code=404,
            detail=f"MCP Server 不存在: {tool.server_name}",
        )

    result = McpClient().call_tool(
        server=server,
        tool_name=tool.tool_name,
        full_name=tool.full_name,
        arguments=payload.arguments,
    )

    return result.model_dump(mode="json")
