# Crypto Market Intelligence Pipeline

## Project Overview
A robust Python ETL (Extract, Transform, Load) pipeline that fetches real-world crypto data (prices, news, social sentiment), normalizes it, and simultaneously persists it to relational (PostgreSQL) and business (Google Sheets) sinks. It also evaluates the data in real-time to trigger Slack alerts based on specific business logic (e.g., >5% price movement).

### Architecture
```text
[CoinCap API]      [News API]    [Fear & Greed API]
       \              |              /
        \             |             /
         ▼            ▼            ▼
    [Python ETL Pipeline (src/)]
    - Fetches data hourly
    - Cleans + merges data
    - Calculates daily metrics & price deltas
         │
         ├──→ Google Sheets (Business/Client view)
         ├──→ PostgreSQL (Analytical/Engineer view)
         └──→ Slack App/Webhook (Alerts on >5% price change)
```

---

## Prerequisites (Accounts & Keys needed)
Before writing code, you need to sign up for these free services and get API keys:
1. **CoinCap API**: Free crypto market prices from CoinCap v2.
2. **News API (newsapi.org)**: Free tier account for finance/crypto news.
3. **Alternative.me Fear & Greed API**: Free endpoint for market sentiment.
4. **Google Cloud Console**: Follow a guide to enable Google Sheets API and create a Service Account JSON credentials file.
5. **Slack**: Create a free Slack workspace (if you don't have one) and set up an Incoming Webhook URL.
6. **Docker Desktop**: For running PostgreSQL locally without a complex installation.

---

## Phase 1: Project & Environment Setup

### 1. Structure the Project
Create the following directory structure:
```text
python-api-automation/
├── .env                 # API Keys and Secrets (DO NOT COMMIT)
├── .env.example         # Template for .env
├── .gitignore           # Ignore .env, venv, __pycache__, service-account.json
├── docker-compose.yml   # PostgreSQL setup
├── requirements.txt     # Python dependencies
├── credentials/         # Store Google sheets json here
└── src/
    ├── __init__.py
    ├── main.py          # Orchestrator script
    ├── extract/         # API ingestion modules
    ├── transform/       # Data cleaning modules
    ├── load/            # Database and Sheets insertion
    └── notify/          # Slack integration
```

### 2. Python Environment
```bash
python3 -m venv venv
source venv/bin/activate
# Install core packages
pip install requests psycopg2-binary sqlalchemy gspread oauth2client python-dotenv schedule pandas
pip freeze > requirements.txt
```

### 3. Local PostgreSQL Setup (`docker-compose.yml`)
Create a Docker compose file to spin up a local DB and admin panel (pgAdmin). Run `docker-compose up -d` to start it.
Write initial SQL scripts to create tables: `crypto_prices`, `news_headlines`, `fear_greed_index`.

---

## Phase 2: The Extract Layer (API Ingestion)

Code lives in `src/extract/`:
1. **`coincap.py`**: Write a function to fetch current prices, 24h trading volume, and 24h percentage change for Bitcoin, Ethereum, and Solana.
2. **`news_api.py`**: Write a function to fetch the top 5 recent news headlines mentioning "Crypto", "Bitcoin", or "Ethereum".
3. **`fear_greed.py`**: Use `requests` to fetch the latest Fear & Greed Index from `https://api.alternative.me/fng/`.

---

## Phase 3: The Transform Layer (Data Processing)

Code lives in `src/transform/`:
1. **`process.py`**:
   - Accept the raw JSON from the 3 extractors.
   - Standardize timestamps (ISO 8601).
   - Ensure all prices are converted to floats.
   - **Business Logic**: Evaluate the `changePercent24Hr` from CoinCap. If `abs(change) > 5.0`, flag this asset for a Slack alert.

---

## Phase 4: The Load Layer (Data Persistence)

Code lives in `src/load/`:
1. **`postgres.py`**:
   - Use `sqlalchemy` to connect to the local Docker PostgreSQL database.
   - Insert the cleaned CoinCap, News, and Fear & Greed data into their respective tables.
2. **`sheets.py`**:
   - Use `gspread` and your GCP Service Account JSON to authenticate.
   - Open a specific Google Sheet by its ID/URL.
   - Append the new cleaned data as rows to the sheet (e.g., Tab 1: Prices, Tab 2: News).

---

## Phase 5: The Notification Layer

Code lives in `src/notify/`:
1. **`slack.py`**:
   - Accept an alert payload (e.g., "🚨 Bitcoin dropped by 6.2% in the last 24h!").
   - Format a JSON payload compatible with Slack's Block Kit or basic text structure.
   - Make a `POST` request to your Slack Webhook URL.

---

## Phase 6: Orchestration & Automation

Code lives in `src/main.py`:
1. Import all your modules.
2. Build the main execution flow:
   ```python
   def run_pipeline():
       print("Starting pipeline run...")
       # 1. Extract
       prices = extract.coincap.get_prices()
       # 2. Transform
       clean_prices, alerts = transform.process.clean_data(prices)
       # 3. Load
       load.postgres.insert_prices(clean_prices)
       load.sheets.append_prices(clean_prices)
       # 4. Notify
       if alerts:
           notify.slack.send_alerts(alerts)
       print("Pipeline run complete.")
   ```
3. **Automation**: Use the `schedule` package to run this function every hour forever:
   ```python
   import schedule
   import time

   schedule.every().hour.do(run_pipeline)
   while True:
       schedule.run_pending()
       time.sleep(60)
   ```

---

## Next Steps for You
1. Obtain all the required API Keys mentioned in the **Prerequisites**.
2. Put the API keys into a `.env` file.
3. Once you have the keys, we can start writing the actual Python code module by module.
