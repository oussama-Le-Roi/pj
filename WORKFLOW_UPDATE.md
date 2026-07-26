# Workflow update (apply manually)

GitHub blocks the Arena GitHub App from editing files under `.github/workflows/`,
so please paste the block below into `.github/workflows/bot.yml` yourself.

## Near real-time bot (recommended)

Each run stays alive and long-polls Telegram for ~5 minutes, so replies are
instant while the run is active. The schedule starts a new run every 5 minutes,
giving continuous coverage.

```yaml
name: 🤖 Telegram AI Bot
on:
  schedule:
    - cron: '*/5 * * * *'
  workflow_dispatch:

concurrency:
  group: telegram-bot
  cancel-in-progress: false

jobs:
  run-bot:
    name: Process Messages
    runs-on: ubuntu-latest
    timeout-minutes: 7          # must exceed RUN_DURATION
    steps:
      - name: 📥 Checkout code
        uses: actions/checkout@v4

      - name: 🐍 Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: 📦 Install dependencies
        run: pip install -r requirements.txt

      - name: 🤖 Run bot
        env:
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
          RUN_DURATION: '290'   # listen ~4m50s, then exit cleanly
        run: python bot.py
```

## Notes

- `RUN_DURATION=0` (or unset) keeps the old behaviour: drain the backlog once and exit.
- GitHub's cron is best-effort and often runs late under load, so there can still be
  gaps between runs. For true 24/7 instant replies, host the bot somewhere that allows
  a long-running process (see README "Always-on hosting").
