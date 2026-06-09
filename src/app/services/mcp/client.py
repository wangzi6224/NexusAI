from __future__ import annotations

import asyncio
from time import perf_counter
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from src.app.services.mcp.schemas import McpServerConfig, McpToolCallResult


class McpClient:
    """MCP Client。

    负责连接外部 MCP Server，并调用指定工具。
    第一版每次调用建立连接，简单可靠。
    Week 25 可以升级连接池、超时、取消、重试。
    """

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
            params = StdioServerParameters(
                command=server.command,
                args=server.args,
                env=server.env or None,
            )

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

    def _stringify_result(self, result: Any) -> str:
        if isinstance(result, str):
            return result
        return str(result)
