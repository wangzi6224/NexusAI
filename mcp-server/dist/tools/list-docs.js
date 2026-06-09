"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.listDocsTool = listDocsTool;
const backend_client_js_1 = require("../backend-client.js");
async function listDocsTool() {
    const client = new backend_client_js_1.BackendClient();
    const result = await client.post("/internal/mcp/tools/list-docs", {});
    return {
        content: [
            {
                type: "text",
                text: JSON.stringify(result, null, 2),
            },
        ],
    };
}
