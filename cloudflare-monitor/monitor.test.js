import test from 'node:test';
import assert from 'node:assert/strict';
import { inspectFrame, checkApp, APP_URL, MAX_BROWSER_MS } from './monitor.js';

test('ready app is recognized without clicking any button', async () => {
  const original = globalThis.document;
  let clicks = 0;
  globalThis.document = { querySelectorAll: () => [{ textContent: 'Process documents', getClientRects: () => [1], click: () => clicks++ }] };
  try {
    assert.equal(await inspectFrame({ evaluate: fn => fn() }), 'ready');
    assert.equal(clicks, 0);
  } finally { globalThis.document = original; }
});

test('only the explicit sleep button is clicked', async () => {
  const original = globalThis.document;
  const clicks = [];
  globalThis.document = { querySelectorAll: () => ['Generate answer', 'Yes, get this app back up!'].map(text => ({ textContent: text, getClientRects: () => [1], click: () => clicks.push(text) })) };
  try {
    assert.equal(await inspectFrame({ evaluate: fn => fn() }), 'waking');
    assert.deepEqual(clicks, ['Yes, get this app back up!']);
  } finally { globalThis.document = original; }
});

test('checker inspects iframe and uses only the fixed public app URL', async () => {
  let url;
  const result = await checkApp({ newPage: async () => ({ goto: async u => { url = u; }, frames: () => [{ evaluate: async () => 'loading' }, { evaluate: async () => 'ready' }] }) });
  assert.equal(url, APP_URL);
  assert.equal(result.ok, true);
  assert.equal(MAX_BROWSER_MS * 6, 360_000);
});
