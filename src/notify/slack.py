from __future__ import annotations

from collections.abc import Sequence

import requests

from src.config import settings


def send_alerts(alerts: Sequence[dict]) -> None:
    if not settings.slack_webhook_url or not alerts:
        return

    lines = [
        (
            f"{alert['asset_name']} ({alert['symbol']}) moved "
            f"{alert['change_24h_percent']:.2f}% in 24h. "
            f"Current price: ${alert['price_usd']:,.2f}"
        )
        for alert in alerts
    ]

    response = requests.post(
        settings.slack_webhook_url,
        json={"text": "Crypto market alert:\n" + "\n".join(lines)},
        timeout=20,
    )
    response.raise_for_status()
