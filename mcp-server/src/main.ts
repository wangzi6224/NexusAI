import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

import { listDocsTool } from "./tools/list-docs.js";
import { searchDocsSchema, searchDocsTool } from "./tools/search-docs.js";
import { readDocSchema, readDocTool } from "./tools/read-doc.js";

const server = new McpServer({
  name: "nexusai-mcp-server",
  version: "0.1.0",
});

server.registerTool(
  "list_docs",
  {
    description: "列出 NexusAI 知识库中的文档。只读工具，不修改任何数据。",
    inputSchema: z.object({}).strict(),
  },
  async () => listDocsTool(),
);

server.registerTool(
  "search_docs",
  {
    description: "根据问题检索 NexusAI 知识库文档片段。只读工具。",
    inputSchema: z.object(searchDocsSchema).strict(),
  },
  async (args) => searchDocsTool(args),
);

server.registerTool(
  "read_doc",
  {
    description: "读取指定 NexusAI 文档内容。只读工具。",
    inputSchema: z.object(readDocSchema).strict(),
  },
  async (args) => readDocTool(args),
);

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((error) => {
  console.error("[nexusai-mcp-server] fatal error", error);
  process.exit(1);
});
