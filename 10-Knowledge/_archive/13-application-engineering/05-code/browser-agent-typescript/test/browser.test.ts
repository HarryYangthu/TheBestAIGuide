import test from 'node:test';
import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { readFile, mkdir, rm } from 'node:fs/promises';
import { join } from 'node:path';
import { chromium } from 'playwright';
import { FixtureAgent } from '../src/actions.js';
import { Policy, digest, type Action } from '../src/policy.js';
import { loadState } from '../src/state.js';

async function fixture(name: string, fn: (ctx: Awaited<ReturnType<typeof setup>>) => Promise<void>) {
  const ctx = await setup(name);
  try { await fn(ctx); assert.deepEqual(ctx.errors, [], 'browser has no JavaScript errors'); }
  finally { await ctx.browser.close(); await new Promise<void>((resolve, reject) => ctx.server.close(e => e ? reject(e) : resolve())); }
}
async function setup(name: string) {
  const html = await readFile('fixtures/index.html');
  const server = createServer((_req, res) => { res.setHeader('Content-Type', 'text/html; charset=utf-8'); res.end(html); });
  await new Promise<void>(resolve => server.listen(0, '127.0.0.1', resolve));
  const addr = server.address();
  assert.ok(addr && typeof addr !== 'string');
  const origin = `http://127.0.0.1:${addr.port}`;
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1100, height: 850 }, serviceWorkers: 'block' });
  // Only local fixture traffic. Policy also checks every action's current page origin.
  await context.route('**/*', route => new URL(route.request().url()).origin === origin ? route.continue() : route.abort());
  const page = await context.newPage();
  const errors: string[] = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('console', msg => { if (msg.type() === 'error') errors.push(msg.text()); });
  await page.goto(origin);
  assert.equal(await page.getByRole('heading').textContent(), 'Local task board');
  const dir = join('artifacts', name); await rm(dir, { recursive: true, force: true }); await mkdir(dir, { recursive: true });
  return { page, browser, server, origin, dir, errors };
}
const fill: Action = { id: 'fill-1', kind: 'fill', label: 'Task', value: 'Read the source paper' };
const submit: Action = { id: 'submit-1', kind: 'submit', title: 'Read the source paper' };

test('successful UI update, screenshot evidence, immutable action and permission boundary', async () => {
  await fixture('success', async ({ page, origin, dir }) => {
    const policy = new Policy(origin, new Set([digest(submit)]));
    assert.throws(() => policy.allowUrl('https://example.com'), /ORIGIN_DENIED/);
    assert.throws(() => new Policy(origin).check(submit), /APPROVAL_REQUIRED/);
    assert.throws(() => policy.check({ ...submit, title: 'Changed' }), /APPROVAL_REQUIRED/);
    const deniedAgent = new FixtureAgent(page, new Policy(origin), join(dir, 'denied-state.json'), dir);
    await assert.rejects(deniedAgent.run('denied', [fill, submit]), /APPROVAL_REQUIRED/);
    assert.equal(await page.locator('#tasks li').count(), 0);
    const agent = new FixtureAgent(page, policy, join(dir, 'state.json'), dir);
    const state = await agent.run('run-success', [fill, submit]);
    assert.equal(state.actions['submit-1']?.status, 'completed');
    assert.equal(await page.locator('#tasks li').count(), 1);
    assert.equal(await page.locator('#tasks li').textContent(), submit.title);
    assert.ok((await readFile(join(dir, 'submit-1.png'))).length > 1000);
    await assert.rejects(agent.run('run-success', [{ ...fill, value: 'Changed' }]), /ACTION_CHANGED/);
  });
});
test('resume after action succeeded but checkpoint was not committed', async () => {
  await fixture('recovery', async ({ page, origin, dir }) => {
    const policy = new Policy(origin, new Set([digest(submit)]));
    const path = join(dir, 'state.json');
    const agent = new FixtureAgent(page, policy, path, dir);
    await assert.rejects(agent.run('run-recovery', [fill, submit], { crashAfterId: 'submit-1' }), /SIMULATED_CRASH/);
    assert.equal((await loadState(path, 'run-recovery')).actions['submit-1']?.status, 'pending');
    await page.reload();
    const resumed = new FixtureAgent(page, policy, path, dir);
    const state = await resumed.run('run-recovery', [fill, submit]);
    assert.equal(await page.locator('#tasks li').count(), 1);
    assert.equal(state.actions['submit-1']?.attempts, 2);
    assert.equal(state.actions['submit-1']?.status, 'completed');
  });
});
test('failed locator can recover; cancellation prevents the next action', async () => {
  await fixture('timeout', async ({ page, origin, dir }) => {
    const agent = new FixtureAgent(page, new Policy(origin), join(dir, 'state.json'), dir);
    await page.locator('#task').evaluate(node => node.setAttribute('disabled', ''));
    await assert.rejects(agent.run('run-timeout', [fill]), /Timeout/);
    assert.equal((await loadState(join(dir, 'state.json'), 'run-timeout')).actions['fill-1']?.status, 'failed');
    await page.locator('#task').evaluate(node => node.removeAttribute('disabled'));
    assert.equal((await agent.run('run-timeout', [fill])).actions['fill-1']?.status, 'completed');
    const signal = AbortSignal.abort();
    await assert.rejects(agent.run('run-timeout', [submit], { signal }), /CANCELLED/);
    assert.equal(await page.locator('#tasks li').count(), 0);
  });
});
