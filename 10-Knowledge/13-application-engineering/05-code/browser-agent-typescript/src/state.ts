import { readFile, mkdir, writeFile, rename } from 'node:fs/promises';
import { dirname } from 'node:path';
export type Entry = { digest: string; status: 'pending'|'completed'|'failed'; attempts: number; evidence?: string; error?: string };
export type State = { version: 1; runId: string; actions: Record<string, Entry> };
export async function loadState(path: string, runId: string): Promise<State> {
  try {
    const state: State = JSON.parse(await readFile(path, 'utf8'));
    if (state.version !== 1 || state.runId !== runId || !state.actions || typeof state.actions !== 'object') {
      throw new Error('STATE_MISMATCH');
    }
    return state;
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === 'ENOENT') return { version: 1, runId, actions: {} };
    throw error;
  }
}
export async function saveState(path: string, state: State): Promise<void> {
  await mkdir(dirname(path), { recursive: true });
  // Atomic replacement for one writer. This is not a distributed lock or fsync durability guarantee.
  const temporary = `${path}.tmp`;
  await writeFile(temporary, JSON.stringify(state, null, 2));
  await rename(temporary, path);
}
