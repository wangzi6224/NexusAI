"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const mcp_js_1 = require("@modelcontextprotocol/sdk/server/mcp.js");
const stdio_js_1 = require("@modelcontextprotocol/sdk/server/stdio.js");
const zod_1 = require("zod");
const list_docs_js_1 = require("./tools/list-docs.js");
const search_docs_js_1 = require("./tools/search-docs.js");
const read_doc_js_1 = require("./tools/read-doc.js");
const server = new mcp_js_1.McpServer({
    name: "nexusai-mcp-server",
    version: "0.1.0",
});
server.tool({
    name: "list_docs",
    description: "列出 NexusAI 知识库中的文档。只读工具，不修改任何数据。",
    inputSchema: zod_1.z.object({}).strict(),
}, async () => (0, list_docs_js_1.listDocsTool)());
server.tool({
    name: "search_docs",
    description: "根据问题检索 NexusAI 知识库文档片段。只读工具。",
    inputSchema: zod_1.z.object(search_docs_js_1.searchDocsSchema).strict(),
}, async (args) => (0, search_docs_js_1.searchDocsTool)(args));
server.tool({
    name: "read_doc",
    description: "读取指定 NexusAI 文档内容。只读工具。",
    inputSchema: zod_1.z.object(read_doc_js_1.readDocSchema).strict(),
}, async (args) => (0, read_doc_js_1.readDocTool)(args));
async function main() {
    const transport = new stdio_js_1.StdioServerTransport();
    await server.connect(transport);
}
main().catch((error) => {
    console.error("[nexusai-mcp-server] fatal error", error);
    process.exit(1);
});
