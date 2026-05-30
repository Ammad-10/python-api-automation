# Crypto + News API Automation

Containerised Python ETL pipeline that pulls **crypto prices (CoinCap)**, **news headlines (NewsAPI)**, and the **Fear & Greed Index**, lands them in PostgreSQL, reports to Google Sheets, and pushes price alerts to Slack — on an hourly schedule.

Built to demonstrate a clean, **production-shaped** ETL: typed extractors, idempotent loads, dry-run mode, dockerised infrastructure, and config via `.env`.

---

## Why this exists

Most "API automation" examples are one-off scripts. This repo is a small but complete pattern you can fork for any multi-source pipeline:

- separate `extract / transform / load / notify` packages
- dry-run and skip-flags so you can iterate safely without writing or paging anyone
- PostgreSQL bootstrap SQL in `db/init/` so a fresh container starts ready
- credentials never committed — `credentials/` and `.env` are git-ignored

---

## Architecture

```
   CoinCap ─┐
   NewsAPI ─┼─►  extract/   ─►  transform/   ─►  load/postgres   ─►  PostgreSQL
   F&G Idx ─┘                                     load/sheets    ─►  Google Sheets
                                                  notify/slack   ─►  Slack alerts
```

---

## Stack

| Layer | Tech |
|---|---|
| Language | Python 3 |
| Storage | PostgreSQL 16 (Docker) |
| Reporting | Google Sheets API |
| Alerts | Slack webhooks |
| Sources | CoinCap, NewsAPI, Alternative.me Fear & Greed |
| Packaging | Docker Compose |

---

## Quick start

```bash
# 1. Python env
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Config
cp .env.example .env
# fill in COINCAP_API_KEY, NEWS_API_KEY, SLACK_WEBHOOK_URL, GOOGLE_SHEET_ID

# 3. Local database
docker compose up -d
# PostgreSQL → localhost:5432
# pgAdmin    → http://localhost:5050

# 4. Run
python -m src.main --check --skip-sheets   # sanity check
python -m src.main --once --dry-run        # extract only, no writes
python -m src.main --once                  # one full cycle
python -m src.main                         # hourly loop
```

Useful flags:

- `--skip-sheets` — skip Google Sheets writes while iterating
- `--skip-slack` — silence Slack alerts during testing
- `--dry-run` — extract only, no DB / Sheets / Slack writes

---

## Required environment

```env
COINCAP_API_KEY=your_coincap_bearer_token
NEWS_API_KEY=your_news_api_key
SLACK_WEBHOOK_URL=your_slack_webhook
GOOGLE_SHEET_ID=your_google_sheet_id
```

Share the Google Sheet with the service-account email from your JSON file in `credentials/`.

---

## Repository structure

```
.
├── docker-compose.yml
├── requirements.txt
├── db/init/001_create_tables.sql     # PostgreSQL bootstrap
├── credentials/                       # service-account JSON (gitignored)
└── src/
    ├── main.py                        # CLI + scheduler
    ├── config.py
    ├── extract/                       # CoinCap, NewsAPI, Fear & Greed
    ├── transform/process.py
    ├── load/                          # PostgreSQL, Google Sheets
    └── notify/slack.py
```

---

## Author

**Ammad Ajaz** — cloud data & AI engineer
[github.com/Ammad-10](https://github.com/Ammad-10) · [linkedin.com/in/ammadajaz](https://linkedin.com/in/ammadajaz)
