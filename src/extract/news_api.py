from __future__ import annotations

from typing import Any

import requests

from src.config import settings


API_URL = "https://newsapi.org/v2/everything"


def get_headlines(query: str = "crypto OR bitcoin OR ethereum") -> list[dict[str, Any]]:
    if not settings.news_api_key:
        return []

    response = requests.get(
        API_URL,
        params={
            "q": query,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 5,
            "apiKey": settings.news_api_key,
        },
        timeout=20,
    )
    response.raise_for_status()
    return response.json().get("articles", [])
