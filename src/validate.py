from __future__ import annotations

from pathlib import Path

from src.config import settings


def format_setup_issues(issues: list[str]) -> str:
    return "Setup issues:\n" + "\n".join(f"- {issue}" for issue in issues)


def validate_setup(
    require_database: bool = True,
    require_sheets: bool = False,
    require_slack: bool = True,
) -> list[str]:
    issues: list[str] = []

    if not settings.news_api_key:
        issues.append("NEWS_API_KEY is missing in .env")

    if require_slack and not settings.slack_webhook_url:
        issues.append("SLACK_WEBHOOK_URL is missing in .env")

    credentials_path = Path(settings.google_sheets_credentials_file)
    if require_sheets:
        if not settings.google_sheet_id:
            issues.append("GOOGLE_SHEET_ID is missing in .env")
        elif "@" in settings.google_sheet_id:
            issues.append(
                "GOOGLE_SHEET_ID contains an email address. Use the Sheet ID from "
                "the Google Sheets URL, not the service account email."
            )
        if not credentials_path.exists():
            issues.append(
                f"Google credentials file not found: {settings.google_sheets_credentials_file}"
            )

    if require_database:
        for key, value in {
            "POSTGRES_HOST": settings.postgres_host,
            "POSTGRES_PORT": settings.postgres_port,
            "POSTGRES_DB": settings.postgres_db,
            "POSTGRES_USER": settings.postgres_user,
            "POSTGRES_PASSWORD": settings.postgres_password,
        }.items():
            if not value:
                issues.append(f"{key} is missing in .env")

    return issues
