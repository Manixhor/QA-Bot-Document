// Requires Playwright and a running Streamlit server. No Groq API key is needed.
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
(async () => {
  const browser = await chromium.launch({ headless: true,
    ...(process.env.PLAYWRIGHT_EXECUTABLE_PATH ? { executablePath: process.env.PLAYWRIGHT_EXECUTABLE_PATH } : {}) });
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
    page.setDefaultTimeout(15000);
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.goto(process.env.QA_TEST_URL || 'http://127.0.0.1:8503');
    console.log('Preview loaded');
    await page.getByRole('button', { name: 'What is Python?', exact: true }).click();
    await page.waitForFunction(() => document.querySelector('textarea')?.value === 'What is Python?');
    await page.getByText('Include sample library', { exact: true }).click();
    await page.getByText('Document library · 0 files', { exact: true }).waitFor();
    await page.locator('input[type=file]').setInputFiles({ name: 'release.txt', mimeType: 'text/plain',
      buffer: Buffer.from('The Folio release code is AZURE-742. The release coordinator is Morgan. The launch is planned for November.') });
    await page.getByText('Document library · 1 file', { exact: true }).waitFor();
    console.log('Upload selected');
    await page.getByRole('button', { name: 'Process documents', exact: true }).click();
    await page.getByText('Source search', { exact: true }).click();
    const search = page.getByRole('button', { name: 'Search documents ↗', exact: true });
    await search.waitFor();
    await page.waitForFunction(() => [...document.querySelectorAll('button')].some(button => button.textContent.includes('Search documents') && !button.disabled), null, { timeout: 120000 });
    await page.getByRole('textbox', { name: 'Your question', exact: true }).fill('What is the Folio release code?');
    console.log('Index ready');
    await search.click();
    const source = page.getByText('[1] release.txt', { exact: true });
    await source.click();
    await page.getByText('The Folio release code is AZURE-742.', { exact: false }).waitFor();
    console.log('Source passage verified');
    const download = page.waitForEvent('download');
    await page.getByRole('button', { name: 'Download conversation' }).click();
    assert.equal((await download).suggestedFilename(), 'qa-bot-analysis.txt');
    console.log('Download verified');
    await page.waitForFunction(() => !document.querySelector('[data-stale="true"]'));
    for (const width of [320, 375, 768, 1440]) {
      await page.setViewportSize({ width, height: 1000 });
      // Close the overlay sidebar when switching down from desktop.
      const close = page.locator('[data-testid="stSidebarCollapseButton"] button');
      if (width < 640 && await close.isVisible()) await close.click();
      assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), `overflow at ${width}`);
      await page.evaluate(() => document.querySelector('[data-testid="stMain"]')?.scrollTo(0, 0));
      if (width === 375 || width === 1440) await page.screenshot({ path: `/private/tmp/qa-bot-${width}.png`, fullPage: true, animations: 'disabled', timeout: 10000 });
    }
    await page.getByRole('button', { name: 'Clear conversation', exact: true }).click();
    await page.getByRole('button', { name: 'What is Python?', exact: true }).waitFor();
    assert.deepEqual(errors, []);
    console.log('Passed: example fill, TXT upload, real embeddings/indexing, source search, evidence, download, clear and 4 viewport widths.');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exit(1); });
