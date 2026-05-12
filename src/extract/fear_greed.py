from __future__ import annotations

from typing import Any

import requests


API_URL = "https://api.alternative.me/fng/"


def get_fear_greed_index(limit: int = 1) -> list[dict[str, Any]]:
    response = requests.get(
        API_URL,
        params={"limit": limit, "format": "json"},
        timeout=20,
    )
    response.raise_for_status()
    return response.json().get("data", [])
