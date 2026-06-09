"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.searchDocsSchema = void 0;
exports.searchDocsTool = searchDocsTool;
const zod_1 = require("zod");
const backend_client_js_1 = require("../backend-client.js");
exports.searchDocsSchema = {
    query: zod_1.z.string().min(1).describe("用于知识库检索的完整问题或关键词"),
    top_k: zod_1.z
        .number()
        .int()
        .min(1)
        .max(20)
        .default(5)
        .describe("最多返回多少条结果"),
    score_threshold: zod_1.z
        .number()
        .min(0)
        .max(1)
        .default(0.3)
        .describe("最低相关性分数"),
};
async function searchDocsTool(args) {
    const client = new backend_client_js_1.BackendClient();
    const result = await client.post("/internal/mcp/tools/search-docs", {
        query: args.query,
        top_k: args.top_k ?? 5,
        score_threshold: args.score_threshold ?? 0.3,
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
