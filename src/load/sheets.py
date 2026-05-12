from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
import re

import gspread
from gspread.exceptions import SpreadsheetNotFound, WorksheetNotFound

from src.config import settings


PRICE_HEADERS = [
    "observed_at",
    "asset_name",
    "symbol",
    "price_usd",
    "volume_24h_usd",
    "change_24h_percent",
]


def _sheet_key(value: str) -> str:
    match = re.search(r"/spreadsheets/d/([^/]+)", value)
    if match:
        return match.group(1)
    return value


def _open_sheet():
    if not settings.google_sheet_id:
        raise RuntimeError(
            "GOOGLE_SHEET_ID is empty. Paste the Sheet ID or full Google Sheets URL "
            "into .env and share the sheet with the service account email."
        )

    credentials_path = Path(settings.google_sheets_credentials_file)
    if not credentials_path.exists():
        raise RuntimeError(
            f"Google credentials file not found: {settings.google_sheets_credentials_file}"
        )

    client = gspread.service_account(filename=str(credentials_path))

    try:
        return client.open_by_key(_sheet_key(settings.google_sheet_id))
    except SpreadsheetNotFound as exc:
        raise RuntimeError(
            "Google Sheet could not be opened. Put the Sheet ID or full Sheet URL "
            "in GOOGLE_SHEET_ID, then share that sheet with the service account "
            "email from your JSON file."
        ) from exc


def _worksheet_with_headers(sheet, title: str, headers: list[str]):
    try:
        worksheet = sheet.worksheet(title)
    except WorksheetNotFound:
        worksheet = sheet.add_worksheet(title=title, rows=1000, cols=len(headers))

    existing_headers = worksheet.row_values(1)
    if existing_headers != headers:
        worksheet.update("A1", [headers])

    return worksheet


def append_prices(rows: Sequence[dict]) -> None:
    sheet = _open_sheet()
    if not rows:
        return

    worksheet = _worksheet_with_headers(sheet, settings.google_sheet_name, PRICE_HEADERS)
    worksheet.append_rows(
        [
            [
                row["observed_at"],
                row["asset_name"],
                row["symbol"],
                row["price_usd"],
                row["volume_24h_usd"],
                row["change_24h_percent"],
            ]
            for row in rows
        ],
        value_input_option="USER_ENTERED",
    )
