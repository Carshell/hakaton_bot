import json
import logging
import os
from typing import Any

from database import get_registration, get_unsynced_registrations, mark_synced

logger = logging.getLogger(__name__)

SHEET_COLUMNS = [
    "registration_date",
    "telegram_user_id",
    "full_name",
    "email",
    "telegram_username",
    "social_media",
    "portfolio_links",
    "occupation",
    "workplace",
    "llm_experience",
    "tools",
    "coolest_project",
    "traffic_source",
    "data_consent",
    "start_payload",
]


def _get_worksheet():
    credentials_path = os.getenv("GOOGLE_CREDENTIALS_PATH")
    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    if not credentials_path or not sheet_id:
        return None

    import gspread
    from google.oauth2.service_account import Credentials

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    credentials = Credentials.from_service_account_file(credentials_path, scopes=scopes)
    client = gspread.authorize(credentials)
    spreadsheet = client.open_by_key(sheet_id)
    worksheet = spreadsheet.sheet1

    existing = worksheet.row_values(1)
    if not existing:
        worksheet.append_row(SHEET_COLUMNS)

    return worksheet


def _row_from_registration(reg: dict[str, Any]) -> list[Any]:
    tools = reg.get("tools") or ""
    if isinstance(tools, str) and tools.startswith("["):
        try:
            tools = ", ".join(json.loads(tools))
        except json.JSONDecodeError:
            pass

    return [
        reg.get("registration_date", ""),
        reg.get("telegram_user_id", ""),
        reg.get("full_name", ""),
        reg.get("email", ""),
        reg.get("telegram_username", ""),
        reg.get("social_media", ""),
        reg.get("portfolio_links", ""),
        reg.get("occupation", ""),
        reg.get("workplace", ""),
        reg.get("llm_experience", ""),
        tools,
        reg.get("coolest_project", ""),
        reg.get("traffic_source", ""),
        "yes" if reg.get("data_consent") else "no",
        reg.get("start_payload", ""),
    ]


async def sync_registration(user_id: int) -> bool:
    reg = get_registration(user_id)
    if not reg or not reg.get("is_completed"):
        return False

    worksheet = _get_worksheet()
    if worksheet is None:
        logger.info("Google Sheets not configured, skipping sync for user %s", user_id)
        return False

    try:
        worksheet.append_row(_row_from_registration(reg), value_input_option="USER_ENTERED")
        mark_synced(user_id)
        return True
    except Exception:
        logger.exception("Failed to sync user %s to Google Sheets", user_id)
        raise


async def backfill_unsynced() -> int:
    worksheet = _get_worksheet()
    if worksheet is None:
        return 0

    synced = 0
    for reg in get_unsynced_registrations():
        try:
            worksheet.append_row(_row_from_registration(reg), value_input_option="USER_ENTERED")
            mark_synced(reg["telegram_user_id"])
            synced += 1
        except Exception:
            logger.exception("Backfill failed for user %s", reg["telegram_user_id"])
    return synced
