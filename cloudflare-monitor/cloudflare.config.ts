import { defineConfig, bindings, triggers } from 'cf/config';
export default defineConfig({
  accountId: 'e9e084124b4e423e6d1c7000631e8d5b',
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
