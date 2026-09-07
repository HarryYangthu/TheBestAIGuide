export interface ToolCall { call_id: string; name: string; arguments: Record<string, unknown> }
export type ToolResult =
  | { call_id: string; ok: true; data: unknown }
  | { call_id: string; ok: false; error: { code: string; retryable: boolean } };
export interface Identity { subject: string; scopes: ReadonlySet<string> }
export interface ToolContext { identity: Identity; signal: AbortSignal }
export interface ToolDefinition {
  inputSchema: object;
  outputSchema: object;
  scope: string;
  handler: (args: Record<string, unknown>, context: ToolContext) => Promise<unknown>;
}
