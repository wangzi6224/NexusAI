export type {
  DiscoverMcpToolsResponse,
  ListResponse,
  McpAuditLog,
  McpAuditLogQuery,
  McpRiskLevel,
  McpServerConfig,
  McpServerCreatePayload,
  McpServerUpdatePayload,
  McpToolCallResult,
  McpToolSpec,
  McpToolUpdatePayload,
  McpTransportType,
} from '@/services/mcpApi';

export interface JsonParseResult {
  ok: boolean;
  value?: Record<string, unknown>;
  error?: string;
}
