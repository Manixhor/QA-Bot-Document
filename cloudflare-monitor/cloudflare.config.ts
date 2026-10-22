import { defineConfig, bindings, triggers } from 'cf/config';
export default defineConfig({
  accountId: '1e5a5507aa6b66ae97f1f85ee3e71c98',
  worker: {
    name: 'qa-bot-availability',
    entrypoint: './index.js',
    compatibilityDate: '2026-10-22',
    compatibilityFlags: ['nodejs_compat'],
    env: { BROWSER: bindings.browser(), CHECK_TOKEN: bindings.secret() },
    triggers: [triggers.scheduled({ schedule: '37 */4 * * *' })],
    workersDev: true,
    observability: { enabled: true, logs: { enabled: true }, traces: { enabled: true } },
  },
});
