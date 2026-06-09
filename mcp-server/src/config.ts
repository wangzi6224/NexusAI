export type McpServerConfig = {
  backendBaseUrl: string;
  backendToken: string;
  requestTimeoutMs: number;
};

export function loadConfig(): McpServerConfig {
  return {
    backendBaseUrl: (
      process.env.NEXUSAI_BACKEND_BASE_URL || "http://127.0.0.1:8000"
    ).replace(/\/$/, ""),
    backendToken: process.env.NEXUSAI_MCP_TOKEN || "",
    requestTimeoutMs: Number(process.env.NEXUSAI_MCP_TIMEOUT_MS || 15000),
  };
}
