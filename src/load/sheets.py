from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import gspread
from gspread.exceptions import WorksheetNotFound

from src.config import settings


PRICE_HEADERS = [
    "observed_at",
    "asset_name",
    "symbol",
    "price_usd",
    "volume_24h_usd",
    "change_24h_percent",
]


def _open_sheet():
    if not settings.google_sheet_id:
        return None

    credentials_path = Path(settings.google_sheets_credentials_file)
    if not credentials_path.exists():
        return None

    client = gspread.service_account(filename=str(credentials_path))
    return client.open_by_key(settings.google_sheet_id)


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
    if not sheet or not rows:
        return

    worksheet = _worksheet_with_headers(sheet, "Prices", PRICE_HEADERS)
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
