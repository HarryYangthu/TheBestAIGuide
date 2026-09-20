import { Ajv2020 } from "ajv/dist/2020.js";
import type { ValidateFunction } from "ajv";
import type { ToolDefinition } from "./contracts.js";

export interface RegisteredTool extends ToolDefinition { validateInput: ValidateFunction; validateOutput: ValidateFunction }
export class Registry {
  private readonly tools = new Map<string, RegisteredTool>();
  private readonly ajv = new Ajv2020({ allErrors: true, strict: true, coerceTypes: false });
  register(name: string, definition: ToolDefinition): void {
    if (!/^[a-zA-Z0-9_.-]+$/.test(name) || this.tools.has(name)) throw new Error("invalid or duplicate tool name");
    const validateInput = this.ajv.compile(definition.inputSchema);
    const validateOutput = this.ajv.compile(definition.outputSchema);
    this.tools.set(name, { ...definition, validateInput, validateOutput });
  }
  get(name: string): RegisteredTool | undefined { return this.tools.get(name); }
}
