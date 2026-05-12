from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


ALERT_THRESHOLD_PERCENT = 5.0


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def clean_prices(raw_prices: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    observed_at = utc_now_iso()
    prices = []
    alerts = []

    for item in raw_prices:
        change = float(item.get("changePercent24Hr") or 0)
        record = {
            "asset_id": item["id"],
            "asset_name": item["name"],
            "symbol": item["symbol"].upper(),
            "price_usd": float(item["priceUsd"]),
            "volume_24h_usd": float(item.get("volumeUsd24Hr") or 0),
            "change_24h_percent": change,
            "observed_at": observed_at,
        }
        prices.append(record)

        if abs(change) > ALERT_THRESHOLD_PERCENT:
            alerts.append(
                {
                    "asset_name": record["asset_name"],
                    "symbol": record["symbol"],
                    "change_24h_percent": change,
                    "price_usd": record["price_usd"],
                }
            )

    return prices, alerts


def clean_news(raw_articles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "source": (article.get("source") or {}).get("name"),
            "title": article.get("title", ""),
            "url": article.get("url"),
            "published_at": article.get("publishedAt"),
        }
        for article in raw_articles
        if article.get("title")
    ]


def clean_fear_greed(raw_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "value": int(item["value"]),
            "classification": item["value_classification"],
            "observed_at": datetime.fromtimestamp(
                float(item["timestamp"]),
                tz=timezone.utc,
            ).isoformat(),
        }
        for item in raw_items
        if item.get("value") and item.get("timestamp")
    ]
