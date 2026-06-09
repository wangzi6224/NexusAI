"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.readDocSchema = void 0;
exports.readDocTool = readDocTool;
const zod_1 = require("zod");
const backend_client_js_1 = require("../backend-client.js");
exports.readDocSchema = {
    document_id: zod_1.z.string().min(1).describe("文档 ID"),
    max_chars: zod_1.z.number().int().min(500).max(20000).default(6000),
};
async function readDocTool(args) {
    const client = new backend_client_js_1.BackendClient();
    const result = await client.post("/internal/mcp/tools/read-doc", {
        document_id: args.document_id,
        max_chars: args.max_chars ?? 6000,
    });
    return {
        content: [
            {
                type: "text",
                text: JSON.stringify(result, null, 2),
            },
        ],
    };
}
