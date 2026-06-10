import { http } from './api';

export type McpRiskLevel = 'low' | 'medium' | 'high';
export type McpTransportType = 'stdio' | 'SSE/HTTP' | 'Streaming HTTP';

export interface McpServerConfig {
  id?: string | null;
  name: string;
  transport: McpTransportType;
  command: string;
  args: string[];
  env: Record<string, string>;
  enabled: boolean;
  timeout_seconds: number;
  metadata: Record<string, unknown>;
  tool_count?: number;
  last_discovered_at?: string | null;
}

export interface McpServerCreatePayload {
  name: string;
  transport: McpTransportType;
  command: string;
  args: string[];
  env: Record<string, string>;
  enabled: boolean;
  timeout_seconds: number;
  metadata: Record<string, unknown>;
}

export interface McpServerUpdatePayload {
  command?: string;
  args?: string[];
  env?: Record<string, string>;
  enabled?: boolean;
  timeout_seconds?: number;
  metadata?: Record<string, unknown>;
}

export interface McpToolSpec {
  id?: string | null;
  server_name: string;
  tool_name: string;
  full_name: string;
  description: string;
  input_schema: Record<string, unknown>;
  risk_level: McpRiskLevel;
  enabled: boolean;
  metadata: Record<string, unknown>;
}

export interface McpToolUpdatePayload {
  description?: string;
  input_schema?: Record<string, unknown>;
  risk_level?: McpRiskLevel;
  enabled?: boolean;
  metadata?: Record<string, unknown>;
}

export interface McpToolCallResult {
  server_name: string;
  tool_name: string;
  full_name: string;
  success: boolean;
  content: string;
  raw_result?: unknown;
  error_code?: string | null;
  error_message?: string | null;
  latency_ms: number;
  metadata: Record<string, unknown>;
}

export interface McpAuditLog {
  id: string;
  assistant_run_id?: string | null;
  agent_run_id?: string | null;
  conversation_id?: string | null;
  server_name: string;
  tool_name: string;
  full_tool_name: string;
  arguments: Record<string, unknown>;
  success: boolean;
  error_code?: string | null;
  error_message?: string | null;
  latency_ms: number;
  result_chars: number;
  risk_level: McpRiskLevel;
  metadata: Record<string, unknown>;
  created_at?: string;
}

export interface ListResponse<T> {
  items: T[];
  count?: number;
}

export interface DiscoverMcpToolsResponse extends ListResponse<McpToolSpec> {
  server_name: string;
  discovered_count: number;
  saved_count: number;
}

export interface McpAuditLogQuery {
  server_name?: string;
  tool_name?: string;
  full_tool_name?: string;
  limit?: number;
}

export async function listMcpServers(): Promise<ListResponse<McpServerConfig>> {
  const { data } = await http.get<ListResponse<McpServerConfig>>('/mcp/servers');
  return data;
}

export async function createMcpServer(
  payload: McpServerCreatePayload,
): Promise<McpServerConfig> {
  const { data } = await http.post<McpServerConfig>('/mcp/servers', payload);
  return data;
}

export async function updateMcpServer(
  serverName: string,
  payload: McpServerUpdatePayload,
): Promise<McpServerConfig> {
  const { data } = await http.patch<McpServerConfig>(
    `/mcp/servers/${encodeURIComponent(serverName)}`,
    payload,
  );
  return data;
}

export async function deleteMcpServer(
  serverName: string,
): Promise<{ id: string; name: string }> {
  const { data } = await http.delete<{ id: string; name: string }>(
    `/mcp/servers/${encodeURIComponent(serverName)}`,
  );
  return data;
}

export async function discoverMcpTools(
  serverName: string,
): Promise<DiscoverMcpToolsResponse> {
  const { data } = await http.post<DiscoverMcpToolsResponse>(
    `/mcp/servers/${encodeURIComponent(serverName)}/discover`,
  );
  return data;
}

export async function listMcpTools(
  serverName?: string,
): Promise<ListResponse<McpToolSpec>> {
  const { data } = await http.get<ListResponse<McpToolSpec>>('/mcp/tools', {
    params: serverName ? { server_name: serverName } : undefined,
  });
  return data;
}

export async function updateMcpTool(
  serverName: string,
  toolName: string,
  payload: McpToolUpdatePayload,
): Promise<McpToolSpec> {
  const fullName = `mcp__${serverName}__${toolName}`;
  const { data } = await http.patch<McpToolSpec>(
    `/mcp/tools/${encodeURIComponent(fullName)}`,
    payload,
  );
  return data;
}

export async function callMcpTool(
  fullName: string,
  argumentsPayload: Record<string, unknown>,
): Promise<McpToolCallResult> {
  const { data } = await http.post<McpToolCallResult>(
    `/mcp/tools/${encodeURIComponent(fullName)}/call`,
    { arguments: argumentsPayload },
  );
  return data;
}

export async function listMcpAuditLogs(
  query: McpAuditLogQuery,
): Promise<ListResponse<McpAuditLog>> {
  // 等待后端补齐：当前 MCP router 尚未暴露审计日志查询接口。
  const { data } = await http.get<ListResponse<McpAuditLog>>('/mcp/audit-logs', {
    params: query,
  });
  return data;
}
