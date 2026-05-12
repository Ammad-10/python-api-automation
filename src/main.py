from __future__ import annotations

import argparse
import sys
import time

import requests
import schedule

from src.extract.coincap import get_prices
from src.extract.fear_greed import get_fear_greed_index
from src.extract.news_api import get_headlines
from src.load.postgres import insert_fear_greed, insert_news, insert_prices
from src.load.sheets import append_prices
from src.notify.slack import send_alerts, send_test_message
from src.transform.process import clean_fear_greed, clean_news, clean_prices
from src.validate import format_setup_issues, validate_setup


def run_pipeline(
    dry_run: bool = False,
    skip_db: bool = False,
    skip_sheets: bool = False,
    skip_slack: bool = False,
) -> None:
    issues = validate_setup(
        require_database=not dry_run and not skip_db,
        require_sheets=not dry_run and not skip_sheets,
        require_slack=not dry_run and not skip_slack,
    )
    if issues:
        raise RuntimeError(format_setup_issues(issues))

    print("Starting pipeline run...")

    raw_prices = get_prices()
    raw_news = get_headlines()
    raw_fear_greed = get_fear_greed_index()

    prices, alerts = clean_prices(raw_prices)
    news = clean_news(raw_news)
    fear_greed = clean_fear_greed(raw_fear_greed)

    if not dry_run and not skip_db:
        insert_prices(prices)
        insert_news(news)
        insert_fear_greed(fear_greed)

    if not dry_run:
        if not skip_sheets:
            append_prices(prices)

        if not skip_slack:
            send_alerts(alerts)

    print(
        "Pipeline run complete: "
        f"{len(prices)} prices, {len(news)} headlines, "
        f"{len(fear_greed)} fear/greed records, {len(alerts)} alerts."
    )


def run_scheduler(skip_db: bool = False, skip_sheets: bool = False, skip_slack: bool = False) -> None:
    run_pipeline(skip_db=skip_db, skip_sheets=skip_sheets, skip_slack=skip_slack)
    schedule.every().hour.do(
        run_pipeline,
        skip_db=skip_db,
        skip_sheets=skip_sheets,
        skip_slack=skip_slack,
    )

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crypto market intelligence ETL")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run the pipeline once and exit.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Fetch and transform data without writing to Postgres, Sheets, or Slack.",
    )
    parser.add_argument(
        "--skip-sheets",
        action="store_true",
        help="Do not write prices to Google Sheets.",
    )
    parser.add_argument(
        "--skip-db",
        action="store_true",
        help="Do not write records to PostgreSQL.",
    )
    parser.add_argument(
        "--skip-slack",
        action="store_true",
        help="Do not send Slack alerts.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate local configuration and exit.",
    )
    parser.add_argument(
        "--test-slack",
        action="store_true",
        help="Send a Slack test message and exit.",
    )
    args = parser.parse_args()

    if args.test_slack:
        try:
            send_test_message()
        except (RuntimeError, requests.RequestException) as exc:
            print(f"Slack test failed: {exc}", file=sys.stderr)
            raise SystemExit(1) from exc
        print("Slack test message sent.")
        raise SystemExit(0)

    if args.check:
        issues = validate_setup(
            require_database=not args.dry_run and not args.skip_db,
            require_sheets=not args.skip_sheets and not args.dry_run,
            require_slack=not args.dry_run and not args.skip_slack,
        )
        if issues:
            print(format_setup_issues(issues))
            raise SystemExit(1)
        print("Setup looks good.")
        raise SystemExit(0)

    if args.once:
        try:
            run_pipeline(
                dry_run=args.dry_run,
                skip_db=args.skip_db,
                skip_sheets=args.skip_sheets,
                skip_slack=args.skip_slack,
            )
        except (RuntimeError, requests.RequestException) as exc:
            print(f"Pipeline failed: {exc}", file=sys.stderr)
            raise SystemExit(1) from exc
    else:
        try:
            run_scheduler(
                skip_db=args.skip_db,
                skip_sheets=args.skip_sheets,
                skip_slack=args.skip_slack,
            )
        except (RuntimeError, requests.RequestException) as exc:
            print(f"Pipeline failed: {exc}", file=sys.stderr)
            raise SystemExit(1) from exc
