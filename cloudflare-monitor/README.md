# QA Bot Cloudflare availability checker

Runs at minute 37 every four hours (UTC) using Cloudflare Cron Triggers and Browser Run. It opens only the public QA Bot, clicks the exact Streamlit sleep button if present, and verifies that Process documents is visible, including inside an iframe. It never processes documents or submits an AI question.

Each browser run has a 60-second deadline and closes the browser in a finally block. Six scheduled runs budget at most six browser minutes daily, excluding launch/close overhead. The account's free browser allowance is shared with other Workers. A slow startup can therefore fail the check; this is best-effort availability, not an uptime guarantee. Check the Worker logs for qa_check success/failure records. There are no automatic retries.

## Deployment

Use Node 22.18+ and the official cf CLI installed here:

```
npm ci
npm run check
npx cf auth login
npx cf deploy --dry-run
npx cf deploy --secrets-file /path/to/private-secrets.json
```

The private JSON must contain CHECK_TOKEN with a randomly generated secret. Never commit it. POST /check requires Authorization: Bearer <CHECK_TOKEN>; no public endpoint launches a browser. Scheduled checks do not need this token. The token is only for an owner-triggered verification.

Keep the existing GitHub schedule until the deployed Cloudflare check passes. Once verified, remove schedule from .github/workflows/qa-bot-availability.yml, leaving manual checks available.
