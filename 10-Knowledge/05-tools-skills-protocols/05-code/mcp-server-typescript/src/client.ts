import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import { fileURLToPath, pathToFileURL } from "node:url";

export async function searchLocal(query = "上下文") {
  const client = new Client({ name: "learning-client", version: "0.1.0" });
  const transport = new StdioClientTransport({ command: process.execPath, args: [fileURLToPath(new URL("./server.js", import.meta.url))] });
  try {
    await client.connect(transport);
    const listing = await client.listTools();
    if (!listing.tools.some(t => t.name === "search_docs")) throw new Error("required tool not advertised");
    const result = await client.callTool({ name: "search_docs", arguments: { query } });
    return { tools: listing.tools.map(t => t.name), result };
  } finally {
    await client.close();
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  console.log(JSON.stringify(await searchLocal(process.argv[2]), null, 2));
}
