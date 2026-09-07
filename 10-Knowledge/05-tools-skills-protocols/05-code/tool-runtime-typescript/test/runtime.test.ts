import test from "node:test";
import assert from "node:assert/strict";
import { Registry } from "../src/registry.js";
import { ToolRuntime } from "../src/runtime.js";
import type { ToolDefinition } from "../src/contracts.js";

const identity = { subject: "learner", scopes: new Set(["docs:read"]) };
const inputSchema = { type: "object", properties: { query: { type: "string", minLength: 1 } }, required: ["query"], additionalProperties: false };
const outputSchema = { type: "object", properties: { count: { type: "integer", minimum: 0 } }, required: ["count"], additionalProperties: false };
function setup(handler: ToolDefinition["handler"] = async () => ({ count: 1 })) {
  const registry = new Registry();
  registry.register("search", { inputSchema, outputSchema, scope: "docs:read", handler });
  return new ToolRuntime(registry);
}
test("input/output contracts and permissions", async () => {
  const runtime = setup();
  assert.deepEqual(await runtime.execute({ call_id: "1", name: "search", arguments: { query: "上下文" } }, identity), { call_id: "1", ok: true, data: { count: 1 } });
  for (const args of [{ query: 1 }, { query: "x", extra: true }, {}]) {
    const r = await runtime.execute({ call_id: "bad", name: "search", arguments: args }, identity);
    assert.equal(!r.ok && r.error.code, "invalid_arguments");
  }
  const denied = await runtime.execute({ call_id: "1", name: "search", arguments: { query: "上下文" } }, { subject: "learner", scopes: new Set() });
  assert.equal(!denied.ok && denied.error.code, "permission_denied");
  const invalid = await setup(async () => ({ count: "one" })).execute({ call_id: "1", name: "search", arguments: { query: "x" } }, identity);
  assert.equal(!invalid.ok && invalid.error.code, "invalid_output");
});
test("concurrent duplicates execute once and conflicts are rejected", async () => {
  let count = 0;
  const runtime = setup(async () => ({ count: ++count }));
  const call = { call_id: "same", name: "search", arguments: { query: "x" } };
  const results = await Promise.all([runtime.execute(call, identity), runtime.execute(call, identity)]);
  assert.equal(count, 1); assert.deepEqual(results[0], results[1]);
  const conflict = await runtime.execute({ ...call, arguments: { query: "y" } }, identity);
  assert.equal(!conflict.ok && conflict.error.code, "idempotency_conflict");
});
test("timeout aborts cooperative handler and is not automatically retryable", async () => {
  let aborted = false;
  const runtime = setup(async (_, { signal }) => new Promise((_, reject) => signal.addEventListener("abort", () => { aborted = true; reject(new Error("stop")); }, { once: true })));
  const result = await runtime.execute({ call_id: "slow", name: "search", arguments: { query: "x" } }, identity, 10);
  assert.equal(!result.ok && result.error.code, "timeout"); assert.ok(aborted);
});
test("caller cancellation propagates", async () => {
  const controller = new AbortController();
  const runtime = setup(async (_, { signal }) => new Promise((_, reject) => signal.addEventListener("abort", () => reject(new Error("stop")), { once: true })));
  const pending = runtime.execute({ call_id: "cancel", name: "search", arguments: { query: "x" } }, identity, 1000, controller.signal);
  setTimeout(() => controller.abort(), 10);
  const result = await pending;
  assert.equal(!result.ok && result.error.code, "cancelled");
});
test("unknown tool and exceptions stay structured", async () => {
  const call = { call_id: "1", name: "search", arguments: { query: "x" } };
  const unknown = await setup().execute({ ...call, name: "absent" }, identity);
  assert.equal(!unknown.ok && unknown.error.code, "unknown_tool");
  const failed = await setup(async () => { throw new Error("private provider token"); }).execute(call, identity);
  assert.equal(!failed.ok && failed.error.code, "execution_error");
  assert.ok(!JSON.stringify(failed).includes("token"));
});
test("caller mutation cannot change validated input or poison cached output", async () => {
  const runtime = setup(async args => ({ count: String(args.query).length }));
  const call = { call_id: "stable", name: "search", arguments: { query: "x" } };
  const pending = runtime.execute(call, identity);
  call.arguments.query = "changed after validation";
  const result = await pending;
  assert.deepEqual(result, { call_id: "stable", ok: true, data: { count: 1 } });
  if (result.ok) (result.data as { count: number }).count = 999;
  const again = await runtime.execute({ ...call, arguments: { query: "x" } }, identity);
  assert.deepEqual(again, { call_id: "stable", ok: true, data: { count: 1 } });
});
test("cancellation before handler scheduling prevents execution", async () => {
  let called = false;
  const controller = new AbortController();
  const runtime = setup(async () => { called = true; return { count: 1 }; });
  const pending = runtime.execute({ call_id: "not-started", name: "search", arguments: { query: "x" } }, identity, 1000, controller.signal);
  controller.abort();
  const result = await pending;
  assert.equal(!result.ok && result.error.code, "cancelled");
  assert.equal(called, false);
});

test("the full ToolCall envelope is checked before any handler executes", async () => {
  let calls = 0;
  const runtime = setup(async () => ({ count: ++calls }));
  const good = {call_id: "valid", name: "search", arguments: {query: "x"}};
  for (const invalid of [null, undefined, [], 7, {...good, call_id: 7}, {...good, call_id: ""},
                         {name: "search", arguments: {}}, {...good, admin: true}]) {
    const result = await runtime.execute(invalid, identity);
    assert.equal(!result.ok && result.error.code, "invalid_request");
    assert.equal(typeof result.call_id, "string");
  }
  assert.equal(calls, 0);
  assert.equal((await runtime.execute(good, identity)).ok, true);
  assert.equal(calls, 1);
});
