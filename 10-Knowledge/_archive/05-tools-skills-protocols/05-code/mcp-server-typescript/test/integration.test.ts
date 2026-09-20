import test from "node:test";
import assert from "node:assert/strict";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { InMemoryTransport } from "@modelcontextprotocol/sdk/inMemory.js";
import { createServer } from "../src/server.js";
import { searchLocal } from "../src/client.js";

test("SDK discovery, arguments, structured data and execution error", async () => {
  const server = createServer();
  const client = new Client({ name: "test", version: "1" });
  const [clientTransport, serverTransport] = InMemoryTransport.createLinkedPair();
  try {
    await server.connect(serverTransport);
    await client.connect(clientTransport);
    const listing = await client.listTools();
    assert.equal(listing.tools[0].name, "search_docs");
    const valid = await client.callTool({ name: "search_docs", arguments: { query: "上下文" } });
    assert.deepEqual(valid.structuredContent, { documents: [{ id: "doc-1", text: "上下文预算为输出和工具结果预留空间。" }] });
    const bad = await client.callTool({ name: "search_docs", arguments: { query: " " } });
    assert.equal(bad.isError, true);
    // The high-level v1 SDK normalizes unknown-tool errors into isError.
    const missing = await client.callTool({ name: "missing", arguments: {} });
    assert.equal(missing.isError, true);
    const wrongType = await client.callTool({ name: "search_docs", arguments: { query: 7 } });
    assert.equal(wrongType.isError, true);
  } finally { await client.close(); await server.close(); }
});
test("real stdio subprocess starts, lists, calls and closes", async () => {
  const response = await searchLocal("工具");
  assert.deepEqual(response.tools, ["search_docs"]);
  assert.equal(response.result.isError ?? false, false);
  assert.ok(JSON.stringify(response.result.structuredContent).includes("doc-2"));
});
