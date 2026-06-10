from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast
from uuid import uuid4

from psycopg import sql

from src.app.db import get_connection
from src.app.services.mcp.client import McpClient
from src.app.services.mcp.schemas import (
    McpServerConfig,
    McpServerCreate,
    McpServerUpdate,
    McpToolCreate,
    McpToolSpec,
    McpToolUpdate,
)


class McpStore:
    """MCP 动态注册配置存储。"""

    def list_servers(self, *, enabled: bool | None = None) -> list[McpServerConfig]:
        where_clause = sql.SQL("")
        params: dict[str, Any] = {}

        if enabled is not None:
            where_clause = sql.SQL("WHERE enabled = %(enabled)s")
            params["enabled"] = enabled

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    sql.SQL(
                        """
                    SELECT *
                    FROM mcp_servers
                    {}
                    ORDER BY created_at DESC
                    """
                    ).format(where_clause),
                    params,
                )
                return [
                    self._server_from_row(self._row_dict(row))
                    for row in cur.fetchall()
                ]

    def get_server(self, name: str) -> McpServerConfig | None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT *
                    FROM mcp_servers
                    WHERE name = %(name)s
                    """,
                    {"name": name},
                )
                row = cur.fetchone()
                return self._server_from_row(self._row_dict(row)) if row else None

    def create_server(self, payload: McpServerCreate) -> McpServerConfig:
        server_id = f"mcp_server_{uuid4().hex}"

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO mcp_servers (
                        id,
                        name,
                        transport,
                        command,
                        args,
                        env,
                        enabled,
                        timeout_seconds,
                        metadata
                    ) VALUES (
                        %(id)s,
                        %(name)s,
                        %(transport)s,
                        %(command)s,
                        %(args)s::jsonb,
                        %(env)s::jsonb,
                        %(enabled)s,
                        %(timeout_seconds)s,
                        %(metadata)s::jsonb
                    )
                    RETURNING *
                    """,
                    {
                        "id": server_id,
                        **payload.model_dump(mode="json"),
                    },
                )
                row = cur.fetchone()
                conn.commit()
                return self._server_from_row(self._required_row(row))

    def update_server(
        self,
        *,
        name: str,
        payload: McpServerUpdate,
    ) -> McpServerConfig:
        current = self.get_server(name)

        if current is None:
            raise ValueError(f"MCP Server 不存在: {name}")

        data = current.model_dump(mode="json")
        patch = payload.model_dump(exclude_unset=True, mode="json")
        data.update(patch)

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE mcp_servers
                    SET
                        command = %(command)s,
                        args = %(args)s::jsonb,
                        env = %(env)s::jsonb,
                        enabled = %(enabled)s,
                        timeout_seconds = %(timeout_seconds)s,
                        metadata = %(metadata)s::jsonb,
                        updated_at = NOW()
                    WHERE name = %(name)s
                    RETURNING *
                    """,
                    data,
                )
                row = cur.fetchone()
                conn.commit()
                return self._server_from_row(self._required_row(row))

    def delete_server(self, name: str) -> dict[str, Any]:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE FROM mcp_servers
                    WHERE name = %(name)s
                    RETURNING id, name
                    """,
                    {"name": name},
                )
                row = cur.fetchone()
                conn.commit()

        if row is None:
            raise ValueError(f"MCP Server 不存在: {name}")

        return self._row_dict(row)

    def list_tools(
        self,
        *,
        server_name: str | None = None,
        enabled: bool | None = None,
    ) -> list[McpToolSpec]:
        conditions: list[sql.SQL] = []
        params: dict[str, Any] = {}

        if server_name is not None:
            conditions.append(sql.SQL("server_name = %(server_name)s"))
            params["server_name"] = server_name

        if enabled is not None:
            conditions.append(sql.SQL("enabled = %(enabled)s"))
            params["enabled"] = enabled

        where_clause = (
            sql.SQL("WHERE {}").format(sql.SQL(" AND ").join(conditions))
            if conditions
            else sql.SQL("")
        )

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    sql.SQL(
                        """
                    SELECT *
                    FROM mcp_tools
                    {}
                    ORDER BY server_name ASC, tool_name ASC
                    """
                    ).format(where_clause),
                    params,
                )
                return [
                    self._tool_from_row(self._row_dict(row))
                    for row in cur.fetchall()
                ]

    def get_tool(self, full_name: str) -> McpToolSpec | None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT *
                    FROM mcp_tools
                    WHERE full_name = %(full_name)s
                    """,
                    {"full_name": full_name},
                )
                row = cur.fetchone()
                return self._tool_from_row(self._row_dict(row)) if row else None

    def create_tool(
        self,
        *,
        server_name: str,
        payload: McpToolCreate,
    ) -> McpToolSpec:
        server = self.get_server(server_name)

        if server is None or server.id is None:
            raise ValueError(f"MCP Server 不存在: {server_name}")

        full_name = payload.full_name or McpClient.build_full_tool_name(
            server_name,
            payload.tool_name,
        )

        tool_id = f"mcp_tool_{uuid4().hex}"

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO mcp_tools (
                        id,
                        server_id,
                        server_name,
                        tool_name,
                        full_name,
                        description,
                        input_schema,
                        risk_level,
                        enabled,
                        metadata
                    ) VALUES (
                        %(id)s,
                        %(server_id)s,
                        %(server_name)s,
                        %(tool_name)s,
                        %(full_name)s,
                        %(description)s,
                        %(input_schema)s::jsonb,
                        %(risk_level)s,
                        %(enabled)s,
                        %(metadata)s::jsonb
                    )
                    RETURNING *
                    """,
                    {
                        "id": tool_id,
                        "server_id": server.id,
                        "server_name": server.name,
                        "tool_name": payload.tool_name,
                        "full_name": full_name,
                        "description": payload.description,
                        "input_schema": payload.input_schema,
                        "risk_level": payload.risk_level,
                        "enabled": payload.enabled,
                        "metadata": payload.metadata,
                    },
                )
                row = cur.fetchone()
                conn.commit()
                return self._tool_from_row(self._required_row(row))

    def update_tool(
        self,
        *,
        full_name: str,
        payload: McpToolUpdate,
    ) -> McpToolSpec:
        current = self.get_tool(full_name)

        if current is None:
            raise ValueError(f"MCP Tool 不存在: {full_name}")

        data = current.model_dump(mode="json")
        patch = payload.model_dump(exclude_unset=True, mode="json")
        data.update(patch)

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE mcp_tools
                    SET
                        description = %(description)s,
                        input_schema = %(input_schema)s::jsonb,
                        risk_level = %(risk_level)s,
                        enabled = %(enabled)s,
                        metadata = %(metadata)s::jsonb,
                        updated_at = NOW()
                    WHERE full_name = %(full_name)s
                    RETURNING *
                    """,
                    data,
                )
                row = cur.fetchone()
                conn.commit()
                return self._tool_from_row(self._required_row(row))

    def upsert_discovered_tools(
        self,
        *,
        server: McpServerConfig,
        tools: list[McpToolSpec],
    ) -> list[McpToolSpec]:
        if server.id is None:
            raise ValueError("server.id 不能为空")

        saved: list[McpToolSpec] = []

        with get_connection() as conn:
            with conn.cursor() as cur:
                for tool in tools:
                    cur.execute(
                        """
                        INSERT INTO mcp_tools (
                            id,
                            server_id,
                            server_name,
                            tool_name,
                            full_name,
                            description,
                            input_schema,
                            risk_level,
                            enabled,
                            metadata,
                            discovered_at
                        ) VALUES (
                            %(id)s,
                            %(server_id)s,
                            %(server_name)s,
                            %(tool_name)s,
                            %(full_name)s,
                            %(description)s,
                            %(input_schema)s::jsonb,
                            %(risk_level)s,
                            %(enabled)s,
                            %(metadata)s::jsonb,
                            NOW()
                        )
                        ON CONFLICT (full_name)
                        DO UPDATE SET
                            description = EXCLUDED.description,
                            input_schema = EXCLUDED.input_schema,
                            metadata = EXCLUDED.metadata,
                            discovered_at = NOW(),
                            updated_at = NOW()
                        RETURNING *
                        """,
                        {
                            "id": f"mcp_tool_{uuid4().hex}",
                            "server_id": server.id,
                            "server_name": server.name,
                            "tool_name": tool.tool_name,
                            "full_name": tool.full_name,
                            "description": tool.description,
                            "input_schema": tool.input_schema,
                            "risk_level": tool.risk_level,
                            "enabled": tool.enabled,
                            "metadata": tool.metadata,
                        },
                    )
                    saved.append(self._tool_from_row(self._required_row(cur.fetchone())))

                conn.commit()

        return saved

    def _server_from_row(self, row: dict[str, Any]) -> McpServerConfig:
        return McpServerConfig(
            id=row["id"],
            name=row["name"],
            transport=row["transport"],
            command=row["command"],
            args=list(row.get("args") or []),
            env=dict(row.get("env") or {}),
            enabled=row["enabled"],
            timeout_seconds=row["timeout_seconds"],
            metadata=dict(row.get("metadata") or {}),
        )

    def _tool_from_row(self, row: dict[str, Any]) -> McpToolSpec:
        return McpToolSpec(
            id=row["id"],
            server_name=row["server_name"],
            tool_name=row["tool_name"],
            full_name=row["full_name"],
            description=row.get("description") or "",
            input_schema=dict(row.get("input_schema") or {}),
            risk_level=row.get("risk_level") or "low",
            enabled=row.get("enabled", True),
            metadata=dict(row.get("metadata") or {}),
        )

    @staticmethod
    def _required_row(row: object | None) -> dict[str, Any]:
        if row is None:
            raise RuntimeError("数据库写入成功但未返回记录")

        return McpStore._row_dict(row)

    @staticmethod
    def _row_dict(row: object) -> dict[str, Any]:
        if isinstance(row, Mapping):
            return dict(row)

        return cast(dict[str, Any], row)
