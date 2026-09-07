import type { Identity, ToolCall, ToolResult } from "./contracts.js";
import { readFileSync } from "node:fs";
import { Ajv2020 } from "ajv/dist/2020.js";
import { Registry } from "./registry.js";

const callSchema = JSON.parse(readFileSync(new URL("../../../shared-schemas/tool-call.schema.json", import.meta.url), "utf8"));
const validateCall = new Ajv2020({ strict: true, allErrors: true, coerceTypes: false }).compile<ToolCall>(callSchema);

function canonical(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(canonical).join(",")}]`;
  if (value !== null && typeof value === "object") {
    return `{${Object.entries(value).sort(([a], [b]) => a.localeCompare(b)).map(([k, v]) => `${JSON.stringify(k)}:${canonical(v)}`).join(",")}}`;
  }
  return JSON.stringify(value);
}

export class ToolRuntime {
  private readonly calls = new Map<string, { signature: string; promise: Promise<ToolResult> }>();
  constructor(private readonly registry: Registry) {}

  async execute(request: unknown, identity: Identity, timeoutMs = 1000, signal?: AbortSignal): Promise<ToolResult> {
    // A malformed request has no trustworthy correlation ID and never enters the cache.
    const suppliedId = request && typeof request === "object" && "call_id" in request ? request.call_id : undefined;
    const requestId = typeof suppliedId === "string" && suppliedId.length > 0 ? suppliedId : "invalid-request";
    const fail = (code: string): ToolResult => ({ call_id: requestId, ok: false, error: { code, retryable: false } });
    if (!validateCall(request)) return fail("invalid_request");
    let call: ToolCall;
    try { call = structuredClone(request); } catch { return fail("invalid_request"); }
    identity = { subject: identity.subject, scopes: new Set(identity.scopes) };
    if (!call.call_id || !identity.subject || !Number.isFinite(timeoutMs) || timeoutMs <= 0) return fail("invalid_request");
    const tool = this.registry.get(call.name);
    if (!tool) return fail("unknown_tool");
    // Authorization is checked even when this call ID has a cached result.
    if (!identity.scopes.has(tool.scope)) return fail("permission_denied");
    if (!tool.validateInput(call.arguments)) return fail("invalid_arguments");
    if (signal?.aborted) return fail("cancelled");
    const key = JSON.stringify([identity.subject, call.call_id]);
    const signature = canonical([call.name, call.arguments]);
    const old = this.calls.get(key);
    if (old) return old.signature === signature ? structuredClone(await old.promise) : fail("idempotency_conflict");
    const promise = this.invoke(call, identity, timeoutMs, signal);
    this.calls.set(key, { signature, promise });
    // JSON-like output is cloned: caller mutation cannot poison the cache.
    return structuredClone(await promise);
  }

  private async invoke(call: ToolCall, identity: Identity, timeoutMs: number, signal?: AbortSignal): Promise<ToolResult> {
    const tool = this.registry.get(call.name)!;
    const controller = new AbortController();
    let timer: ReturnType<typeof setTimeout> | undefined;
    let onCancel: (() => void) | undefined;
    let interruption = "";
    try {
      const interrupted = new Promise<never>((_, reject) => {
        const stop = (code: string) => { interruption = code; controller.abort(); reject(new Error(code)); };
        timer = setTimeout(() => stop("timeout"), timeoutMs);
        onCancel = () => stop("cancelled");
        signal?.addEventListener("abort", onCancel, { once: true });
      });
      const running = Promise.resolve().then(() => {
        controller.signal.throwIfAborted();
        return tool.handler(structuredClone(call.arguments), { identity, signal: controller.signal });
      });
      const data = await Promise.race([running, interrupted]);
      if (!tool.validateOutput(data)) return { call_id: call.call_id, ok: false, error: { code: "invalid_output", retryable: false } };
      return { call_id: call.call_id, ok: true, data: structuredClone(data) };
    } catch {
      return { call_id: call.call_id, ok: false, error: { code: interruption || "execution_error", retryable: false } };
    } finally {
      if (timer) clearTimeout(timer);
      if (onCancel) signal?.removeEventListener("abort", onCancel);
    }
  }
}
