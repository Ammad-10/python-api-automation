from __future__ import annotations

from typing import Any

import requests

from src.config import settings


ASSETS = ("bitcoin", "ethereum", "solana")
API_URL = "https://api.coincap.io/v2/assets"


def get_prices(assets: tuple[str, ...] = ASSETS) -> list[dict[str, Any]]:
    if not settings.coincap_api_key:
        raise RuntimeError("COINCAP_API_KEY is required for CoinCap v2 requests")

    headers = {}
    headers["Authorization"] = f"Bearer {settings.coincap_api_key}"

    response = requests.get(
        API_URL,
        params={"ids": ",".join(assets)},
        headers=headers,
        timeout=20,
    )
    response.raise_for_status()
    return response.json().get("data", [])
