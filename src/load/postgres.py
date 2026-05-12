from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import create_engine, text

from src.config import settings


engine = create_engine(settings.database_url, pool_pre_ping=True)


def _insert_many(statement: str, rows: Sequence[dict]) -> None:
    if not rows:
        return

    with engine.begin() as connection:
        connection.execute(text(statement), list(rows))


def insert_prices(rows: Sequence[dict]) -> None:
    _insert_many(
        """
        INSERT INTO crypto_prices (
            asset_id, asset_name, symbol, price_usd, volume_24h_usd,
            change_24h_percent, observed_at
        )
        VALUES (
            :asset_id, :asset_name, :symbol, :price_usd, :volume_24h_usd,
            :change_24h_percent, :observed_at
        )
        """,
        rows,
    )


def insert_news(rows: Sequence[dict]) -> None:
    _insert_many(
        """
        INSERT INTO news_headlines (source, title, url, published_at)
        VALUES (:source, :title, :url, :published_at)
        """,
        rows,
    )


def insert_fear_greed(rows: Sequence[dict]) -> None:
    _insert_many(
        """
        INSERT INTO fear_greed_index (value, classification, observed_at)
        VALUES (:value, :classification, :observed_at)
        ON CONFLICT (observed_at) DO NOTHING
        """,
        rows,
    )
