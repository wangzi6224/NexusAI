from __future__ import annotations

import asyncio
import json
from time import perf_counter
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from src.app.services.mcp.schemas import McpServerConfig, McpToolCallResult, McpToolSpec


class McpClient:
    """MCP Client。

    负责连接外部 MCP Server，发现工具并调用指定工具。
    第一版每次操作都建立 stdio 连接，简单可靠。
    Week 25 可以升级连接池、超时、取消、重试。
    """

    async def list_tools_async(self, *, server: McpServerConfig) -> list[McpToolSpec]:
        """连接外部 MCP Server，调用 tools/list 发现工具。"""
        try:
            params = self._build_stdio_params(server)
            async with stdio_client(params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await asyncio.wait_for(
                        session.list_tools(),
                        timeout=server.timeout_seconds,
                    )

            tools = getattr(result, "tools", result)
            return [self._to_tool_spec(server=server, tool=tool) for tool in tools]
        except Exception as exc:
            raise RuntimeError(f"MCP tools/list failed: {exc}") from exc

    def list_tools(self, *, server: McpServerConfig) -> list[McpToolSpec]:
        return asyncio.run(self.list_tools_async(server=server))

    async def call_tool_async(
        self,
        *,
        server: McpServerConfig,
        tool_name: str,
        full_name: str,
        arguments: dict[str, Any],
    ) -> McpToolCallResult:
        start = perf_counter()

        try:
            params = self._build_stdio_params(server)

            async with stdio_client(params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await asyncio.wait_for(
                        session.call_tool(tool_name, arguments=arguments),
                        timeout=server.timeout_seconds,
                    )

            content = self._stringify_result(result)
            return McpToolCallResult(
                server_name=server.name,
                tool_name=tool_name,
                full_name=full_name,
                success=True,
                content=content,
                raw_result=result,
                latency_ms=int((perf_counter() - start) * 1000),
            )
        except Exception as exc:
            return McpToolCallResult(
                server_name=server.name,
                tool_name=tool_name,
                full_name=full_name,
                success=False,
                error_code="MCP_TOOL_CALL_FAILED",
                error_message=str(exc),
                latency_ms=int((perf_counter() - start) * 1000),
            )

    def call_tool(
        self,
        *,
        server: McpServerConfig,
        tool_name: str,
        full_name: str,
        arguments: dict[str, Any],
    ) -> McpToolCallResult:
        return asyncio.run(
            self.call_tool_async(
                server=server,
                tool_name=tool_name,
                full_name=full_name,
                arguments=arguments,
            )
        )

    def _build_stdio_params(self, server: McpServerConfig) -> StdioServerParameters:
        if server.transport != "stdio":
            raise ValueError(f"暂不支持的 MCP transport: {server.transport}")

        return StdioServerParameters(
            command=server.command,
            args=server.args,
            env=server.env or None,
        )

    def _to_tool_spec(self, *, server: McpServerConfig, tool: Any) -> McpToolSpec:
        tool_name = str(getattr(tool, "name", "")).strip()
        description = str(getattr(tool, "description", "") or "")
        input_schema = (
            getattr(tool, "inputSchema", None)
            or getattr(tool, "input_schema", None)
            or {"type": "object", "properties": {}}
        )

        if hasattr(input_schema, "model_dump"):
            input_schema = input_schema.model_dump(mode="json")

        if not isinstance(input_schema, dict):
            input_schema = {"type": "object", "properties": {}}

        return McpToolSpec(
            server_name=server.name,
            tool_name=tool_name,
            full_name=self.build_full_tool_name(server.name, tool_name),
            description=description,
            input_schema=input_schema,
            risk_level="low",
            enabled=True,
            metadata={"discovered": True},
        )

    @staticmethod
    def build_full_tool_name(server_name: str, tool_name: str) -> str:
        return f"mcp__{server_name}__{tool_name}"

    def _stringify_result(self, result: Any) -> str:
        if isinstance(result, str):
            return result

        if hasattr(result, "model_dump"):
            return json.dumps(result.model_dump(mode="json"), ensure_ascii=False, default=str)

        return str(result)
