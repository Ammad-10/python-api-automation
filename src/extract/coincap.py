from __future__ import annotations

from typing import Any

import requests

from src.config import settings


ASSETS = ("bitcoin", "ethereum", "solana")
API_URL = "https://api.coincap.io/v2/assets"
FALLBACK_TICKER_URL = "https://api.alternative.me/v2/ticker/"


def _get_fallback_prices(assets: tuple[str, ...]) -> list[dict[str, Any]]:
    response = requests.get(
        FALLBACK_TICKER_URL,
        params={"limit": 50},
        timeout=20,
    )
    response.raise_for_status()

    rows = []
    wanted = set(assets)
    for item in response.json().get("data", {}).values():
        if item.get("website_slug") not in wanted:
            continue

        quote = item.get("quotes", {}).get("USD", {})
        rows.append(
            {
                "id": item["website_slug"],
                "name": item["name"],
                "symbol": item["symbol"],
                "priceUsd": quote.get("price", 0),
                "volumeUsd24Hr": quote.get("volume_24h", 0),
                "changePercent24Hr": quote.get("percentage_change_24h", 0),
            }
        )

    return rows


def get_prices(assets: tuple[str, ...] = ASSETS) -> list[dict[str, Any]]:
    headers = {}
    if settings.coincap_api_key:
        headers["Authorization"] = f"Bearer {settings.coincap_api_key}"

    try:
        response = requests.get(
            API_URL,
            params={"ids": ",".join(assets)},
            headers=headers,
            timeout=20,
        )
        response.raise_for_status()
        return response.json().get("data", [])
    except requests.RequestException:
        return _get_fallback_prices(assets)
