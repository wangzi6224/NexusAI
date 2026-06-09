"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.BackendClient = void 0;
const config_js_1 = require("./config.js");
class BackendClient {
    constructor() {
        this.config = (0, config_js_1.loadConfig)();
    }
    async post(path, body) {
        const controller = new AbortController();
        const timer = setTimeout(() => controller.abort(), this.config.requestTimeoutMs);
        try {
            const response = await fetch(`${this.config.backendBaseUrl}${path}`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${this.config.backendToken}`,
                    "X-NexusAI-Call-Source": "mcp-server",
                },
                body: JSON.stringify(body),
                signal: controller.signal,
            });
            if (!response.ok) {
                const text = await response.text();
                throw new Error(`Backend request failed: ${response.status} ${text}`);
            }
            return (await response.json());
        }
        finally {
            clearTimeout(timer);
        }
    }
}
exports.BackendClient = BackendClient;
