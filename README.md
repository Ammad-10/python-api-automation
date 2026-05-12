# Crypto Market Intelligence Pipeline

Python ETL pipeline for crypto prices, news headlines, Fear & Greed Index,
PostgreSQL storage, Google Sheets reporting, and Slack alerts.

## Project Structure

```text
.
├── .env.example
├── .gitignore
├── docker-compose.yml
├── requirements.txt
├── credentials/
│   └── .gitkeep
├── db/
│   └── init/
│       └── 001_create_tables.sql
└── src/
    ├── config.py
    ├── main.py
    ├── extract/
    │   ├── coincap.py
    │   ├── fear_greed.py
    │   ├── news_api.py
    ├── transform/
    │   └── process.py
    ├── load/
    │   ├── postgres.py
    │   └── sheets.py
    └── notify/
        └── slack.py
```

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Fill in `.env` with your API keys. Keep Google service account JSON files
inside `credentials/`; they are ignored by Git.

Required values before a live run:

```env
COINCAP_API_KEY=your_coincap_bearer_token
NEWS_API_KEY=your_news_api_key
SLACK_WEBHOOK_URL=your_slack_webhook
GOOGLE_SHEET_ID=your_google_sheet_id
```

Share the Google Sheet with the service account email from your JSON file.

## Start Local Database

```bash
docker compose up -d
```

PostgreSQL runs on `localhost:5432`. pgAdmin runs on
`http://localhost:5050`.

## Run

Check local setup:

```bash
python -m src.main --check --skip-sheets
```

Test API extraction without writing anywhere:

```bash
python -m src.main --once --dry-run
```

Run once:

```bash
python -m src.main --once
```

Run hourly:

```bash
python -m src.main
```

Use `--skip-sheets` until `GOOGLE_SHEET_ID` is set. Use `--skip-slack`
when you want to avoid sending alert messages during testing.
