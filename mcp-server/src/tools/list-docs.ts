import { BackendClient } from "../backend-client.js";

export async function listDocsTool() {
  const client = new BackendClient();
  const result = await client.post("/internal/mcp/tools/list-docs", {});

  return {
    content: [
      {
        type: "text" as const,
        text: JSON.stringify(result, null, 2),
      },
    ],
  };
}
