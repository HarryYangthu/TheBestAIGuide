import { mkdir } from 'node:fs/promises';
import { join } from 'node:path';
import type { Page } from 'playwright';
import { digest, Policy, type Action } from './policy.js';
import { loadState, saveState } from './state.js';
export class FixtureAgent {
  constructor(private page: Page, private policy: Policy, private checkpoint: string, private evidenceDir: string) {}
  async run(runId: string, actions: Action[], options: { crashAfterId?: string; signal?: AbortSignal } = {}) {
    const state = await loadState(this.checkpoint, runId);
    await mkdir(this.evidenceDir, { recursive: true });
    for (const action of actions) {
      if (options.signal?.aborted) throw new Error('CANCELLED');
      this.policy.allowUrl(this.page.url());
      this.policy.check(action);
      const previous = state.actions[action.id];
      if (previous && previous.digest !== digest(action)) throw new Error('ACTION_CHANGED');
      if (previous?.status === 'completed') continue;
      const entry = { digest: digest(action), status: 'pending' as const, attempts: (previous?.attempts ?? 0) + 1 };
      state.actions[action.id] = entry;
      await saveState(this.checkpoint, state);
      try {
        if (action.kind === 'fill') {
          await this.page.getByLabel(action.label, { exact: true }).fill(action.value, { timeout: 800 });
        } else {
          const marker = this.page.locator(`[data-action-id="${action.id}"]`).filter({ hasText: action.title });
          // Query external state first: a prior click may have succeeded before our checkpoint.
          if (await marker.count() === 0) {
            const current = await this.page.getByLabel('Task', { exact: true }).inputValue();
            if (current.trim() !== action.title) throw new Error('INPUT_CHANGED');
            await this.page.locator('#submit').evaluate((node, id) => { (node as HTMLElement).dataset.actionId = id; }, action.id);
            await this.page.getByRole('button', { name: 'Add task', exact: true }).click({ timeout: 800 });
            await this.page.locator(`#tasks [data-action-id="${action.id}"]`).waitFor({ state: 'visible', timeout: 800 });
          }
        }
        if (options.crashAfterId === action.id) throw new Error('SIMULATED_CRASH');
        const evidence = `${action.id}.png`;
        await this.page.screenshot({ path: join(this.evidenceDir, evidence), fullPage: true });
        state.actions[action.id] = { ...entry, status: 'completed', evidence };
        await saveState(this.checkpoint, state);
      } catch (error) {
        // A crash leaves pending state. Ordinary errors are visible and retryable with the same action.
        if ((error as Error).message !== 'SIMULATED_CRASH') {
          state.actions[action.id] = { ...entry, status: 'failed', error: (error as Error).message.split('\n')[0] };
          await saveState(this.checkpoint, state);
        }
        throw error;
      }
    }
    return state;
  }
}
