import puppeteer from '@cloudflare/puppeteer';
import { checkApp, MAX_BROWSER_MS } from './monitor.js';

async function run(env) {
  const browser = await puppeteer.launch(env.BROWSER);
  let timer;
  try {
    const result = await Promise.race([
      checkApp(browser),
      new Promise((_, reject) => {
        timer = setTimeout(() => reject(new Error('Browser time budget reached')), MAX_BROWSER_MS);
      }),
    ]);
    console.log(JSON.stringify({ event: 'qa_check', ...result }));
    return result;
  } catch (error) {
    console.error(JSON.stringify({ event: 'qa_check', ok: false, error: String(error) }));
    throw error;
  } finally {
    clearTimeout(timer);
    await browser.close();
  }
}

export default {
  async scheduled(controller, env, ctx) {
    ctx.waitUntil(run(env));
  },
  async fetch(request, env) {
    // Manual checks require a deployment secret; public visitors cannot spend browser quota.
    if (request.method !== 'POST' || new URL(request.url).pathname !== '/check') return new Response('Not found', { status: 404 });
    const provided = new TextEncoder().encode(request.headers.get('Authorization') || '');
    const expected = new TextEncoder().encode(`Bearer ${env.CHECK_TOKEN}`);
    if (!env.CHECK_TOKEN || provided.length !== expected.length || !crypto.subtle.timingSafeEqual(provided, expected)) return new Response('Unauthorized', { status: 401 });
    try { return Response.json(await run(env)); }
    catch { return Response.json({ ok: false, message: 'Check failed; inspect Worker logs' }, { status: 503 }); }
  },
};
