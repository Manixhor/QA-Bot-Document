# QA Bot availability check

GitHub Actions opens the public QA Bot every four hours at minute 17 (UTC), and on manual dispatch. If the Streamlit sleep button appears, the browser clicks it and waits up to five minutes for the Process documents control. It never uploads documents, processes the library, or calls Groq, and needs no API secrets.

See Actions → QA Bot availability for run status and the seven-day screenshot artifact. GitHub's normal workflow failure notifications apply according to your account notification preferences. A screenshot is also attempted when checking fails.

This is best-effort demo availability, not guaranteed uptime. Scheduled runs may be delayed; GitHub disables schedules in public repositories after 60 days without repository activity. Re-enable the workflow in Actions if that happens. Streamlit UI changes may require updating the button labels in the checker.
