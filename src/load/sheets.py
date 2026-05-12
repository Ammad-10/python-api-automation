from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
import re

import gspread
from gspread.exceptions import APIError, SpreadsheetNotFound, WorksheetNotFound

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
    credentials_path = Path(settings.google_sheets_credentials_file)
    if not credentials_path.exists():
        return None

    client = gspread.service_account(filename=str(credentials_path))

    if settings.google_sheet_id:
        try:
            return client.open_by_key(_sheet_key(settings.google_sheet_id))
        except SpreadsheetNotFound:
            pass

    try:
        sheet = client.create(settings.google_sheet_name)
    except APIError as exc:
        raise RuntimeError(
            "Google Sheet could not be opened or created. Put a real Google Sheet "
            "ID or URL in GOOGLE_SHEET_ID, then share that sheet with the service "
            "account email from your JSON file."
        ) from exc

    if settings.google_share_email:
        sheet.share(settings.google_share_email, perm_type="user", role="writer")

    _save_env_value("GOOGLE_SHEET_ID", sheet.id)
    return sheet


def _save_env_value(key: str, value: str) -> None:
    env_path = Path(".env")
    lines = env_path.read_text().splitlines() if env_path.exists() else []
    output = []
    replaced = False

    for line in lines:
        if line.startswith(f"{key}="):
            output.append(f"{key}={value}")
            replaced = True
        else:
            output.append(line)

    if not replaced:
        output.append(f"{key}={value}")

    env_path.write_text("\n".join(output).rstrip() + "\n")


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
