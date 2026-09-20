// Fixed SDK v1.29.0 teaching example: protocol generation 2025-11-25.
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { pathToFileURL } from "node:url";

export function createServer(): McpServer {
  const server = new McpServer({ name: "learning-docs", version: "0.1.0" });
  const documents = [
    { id: "doc-1", text: "上下文预算为输出和工具结果预留空间。" },
    { id: "doc-2", text: "工具超时后需要核查副作用，不能盲目重试。" },
  ];
  server.registerTool("search_docs", {
    description: "在本地教学语料中按子串检索，返回文档ID和原文；无网络访问。",
    inputSchema: { query: z.string().min(1).max(100) },
    outputSchema: { documents: z.array(z.object({ id: z.string(), text: z.string() })) },
  }, async ({ query }) => {
    // A whitespace query is syntactically valid but invalid for this operation.
    if (!query.trim()) return { isError: true, content: [{ type: "text", text: "query must contain non-whitespace characters" }] };
    const result = { documents: documents.filter(d => d.text.includes(query)) };
    return { structuredContent: result, content: [{ type: "text", text: JSON.stringify(result) }] };
  });
  return server;
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const server = createServer();
  // stdout carries JSON-RPC only. Diagnostic logs belong on stderr.
  await server.connect(new StdioServerTransport());
}
