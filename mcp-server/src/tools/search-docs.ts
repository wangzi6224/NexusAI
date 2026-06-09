import { z } from "zod";
import { BackendClient } from "../backend-client.js";

export const searchDocsSchema = {
  query: z.string().min(1).describe("用于知识库检索的完整问题或关键词"),
  top_k: z
    .number()
    .int()
    .min(1)
    .max(20)
    .default(5)
    .describe("最多返回多少条结果"),
  score_threshold: z
    .number()
    .min(0)
    .max(1)
    .default(0.3)
    .describe("最低相关性分数"),
};

export async function searchDocsTool(args: {
  query: string;
  top_k?: number;
  score_threshold?: number;
}) {
  const client = new BackendClient();
  const result = await client.post("/internal/mcp/tools/search-docs", {
    query: args.query,
    top_k: args.top_k ?? 5,
    score_threshold: args.score_threshold ?? 0.3,
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
