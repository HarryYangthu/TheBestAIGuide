import { createHash } from 'node:crypto';
export type Action =
  | { id: string; kind: 'fill'; label: string; value: string }
  | { id: string; kind: 'submit'; title: string };
export function digest(action: Action): string {
  const sorted = Object.fromEntries(Object.entries(action).sort(([a], [b]) => a.localeCompare(b)));
  return createHash('sha256').update(JSON.stringify(sorted)).digest('hex');
}
export class Policy {
  constructor(readonly origin: string, private readonly grants = new Set<string>()) {
    const u = new URL(origin);
    if (u.protocol !== 'http:' || u.hostname !== '127.0.0.1' || u.origin !== origin) {
      throw new Error('LOCAL_ORIGIN_REQUIRED');
    }
  }
  allowUrl(url: string): void {
    if (new URL(url).origin !== this.origin) throw new Error('ORIGIN_DENIED');
  }
  check(action: Action): void {
    if (!/^[a-zA-Z0-9_-]{1,64}$/.test(action.id)) throw new Error('INVALID_ID');
    if (action.kind !== 'fill' && action.kind !== 'submit') throw new Error('UNKNOWN_ACTION');
    if (action.kind === 'fill' && (action.label !== 'Task' || action.value.length > 200)) {
      throw new Error('INPUT_DENIED');
    }
    // Trusted host owns grants. Page text and proposed actions cannot grant access.
    if (action.kind === 'submit' && !this.grants.has(digest(action))) throw new Error('APPROVAL_REQUIRED');
  }
}
