import { z } from "zod";
import { BackendClient } from "../backend-client.js";

export const readDocSchema = {
  document_id: z.string().min(1).describe("文档 ID"),
  max_chars: z.number().int().min(500).max(20000).default(6000),
};

export async function readDocTool(args: {
  document_id: string;
  max_chars?: number;
}) {
  const client = new BackendClient();
  const result = await client.post("/internal/mcp/tools/read-doc", {
    document_id: args.document_id,
    max_chars: args.max_chars ?? 6000,
  });

  return {
    content: [
      {
        type: "text" as const,
        text: JSON.stringify(result, null, 2),
      },
    ],
  };
}
