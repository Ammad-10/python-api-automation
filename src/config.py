from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    coincap_api_key: str | None = os.getenv("COINCAP_API_KEY") or None
    news_api_key: str | None = os.getenv("NEWS_API_KEY") or None
    slack_webhook_url: str | None = os.getenv("SLACK_WEBHOOK_URL") or None
    google_sheets_credentials_file: str = os.getenv(
        "GOOGLE_SHEETS_CREDENTIALS_FILE",
        "credentials/service-account.json",
    )
    google_sheet_id: str | None = os.getenv("GOOGLE_SHEET_ID") or None
    google_sheet_name: str = os.getenv(
        "GOOGLE_SHEET_NAME",
        "Crypto Market Intelligence Pipeline",
    )
    google_share_email: str | None = os.getenv("GOOGLE_SHARE_EMAIL") or None

    postgres_host: str = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port: str = os.getenv("POSTGRES_PORT", "5432")
    postgres_db: str = os.getenv("POSTGRES_DB", "crypto_market")
    postgres_user: str = os.getenv("POSTGRES_USER", "crypto_user")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "crypto_password")

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()
