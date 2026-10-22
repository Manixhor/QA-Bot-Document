export const APP_URL = 'https://app-bot-document-f4vzh3ghty7n23j6gmzbse.streamlit.app/';
export const MAX_BROWSER_MS = 60_000;

// Only inspect known app controls. Never process files or submit AI questions.
export async function inspectFrame(frame) {
  return frame.evaluate(() => {
    const visible = el => !!(el.getClientRects().length);
    const buttons = [...document.querySelectorAll('button')].filter(visible);
    if (buttons.some(el => el.textContent.trim() === 'Process documents')) return 'ready';
    const wake = buttons.find(el => el.textContent.trim() === 'Yes, get this app back up!');
    if (wake) { wake.click(); return 'waking'; }
    return 'loading';
  });
}

export async function checkApp(browser) {
  const page = await browser.newPage();
  await page.goto(APP_URL, { waitUntil: 'domcontentloaded', timeout: 25_000 });
  const deadline = Date.now() + 50_000;
  while (Date.now() < deadline) {
    for (const frame of page.frames()) {
      try {
        if (await inspectFrame(frame) === 'ready') return { ok: true, checkedAt: new Date().toISOString() };
      } catch (error) {
        // A wake-up can replace or detach its frame; retry on the current frames.
        if (!/detached|context|navigation|closed/i.test(String(error))) throw error;
      }
    }
    await new Promise(resolve => setTimeout(resolve, 1500));
  }
  throw new Error('QA Bot interface did not load before the check deadline');
}
