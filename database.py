import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DB_PATH = Path(os.getenv("DATABASE_PATH", "data/bot.db"))


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS registrations (
                telegram_user_id INTEGER PRIMARY KEY,
                current_state TEXT,
                start_payload TEXT,
                registration_date TEXT,
                full_name TEXT,
                email TEXT,
                telegram_username TEXT,
                social_media TEXT,
                portfolio_links TEXT,
                occupation TEXT,
                workplace TEXT,
                llm_experience TEXT,
                tools TEXT,
                coolest_project TEXT,
                traffic_source TEXT,
                data_consent INTEGER DEFAULT 0,
                is_completed INTEGER DEFAULT 0,
                synced_to_sheets INTEGER DEFAULT 0,
                selected_tools TEXT DEFAULT '[]',
                editing_field TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS feedback_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                user_message_id INTEGER NOT NULL,
                admin_message_id INTEGER NOT NULL,
                admin_chat_id INTEGER NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS scheduled_broadcast_log (
                broadcast_id TEXT PRIMARY KEY,
                sent_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        conn.commit()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_registration(user_id: int) -> dict[str, Any] | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM registrations WHERE telegram_user_id = ?",
            (user_id,),
        ).fetchone()
    return dict(row) if row else None


def ensure_registration(user_id: int, start_payload: str | None = None) -> None:
    if not get_registration(user_id):
        create_registration(user_id, start_payload)


def create_registration(user_id: int, start_payload: str | None = None) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO registrations (telegram_user_id, current_state, start_payload)
            VALUES (?, 'welcome', ?)
            ON CONFLICT(telegram_user_id) DO UPDATE SET
                current_state = 'welcome',
                start_payload = COALESCE(excluded.start_payload, registrations.start_payload),
                full_name = NULL,
                email = NULL,
                telegram_username = NULL,
                social_media = NULL,
                portfolio_links = NULL,
                occupation = NULL,
                workplace = NULL,
                llm_experience = NULL,
                tools = NULL,
                coolest_project = NULL,
                traffic_source = CASE
                    WHEN excluded.start_payload IS NOT NULL AND excluded.start_payload != ''
                    THEN excluded.start_payload
                    ELSE NULL
                END,
                data_consent = 0,
                is_completed = 0,
                synced_to_sheets = 0,
                selected_tools = '[]',
                editing_field = NULL,
                registration_date = NULL,
                updated_at = ?
            """,
            (user_id, start_payload, _now()),
        )
        conn.commit()


def update_registration(user_id: int, **fields: Any) -> None:
    if not fields:
        return
    fields["updated_at"] = _now()
    columns = ", ".join(f"{key} = ?" for key in fields)
    values = list(fields.values()) + [user_id]
    with get_connection() as conn:
        conn.execute(
            f"UPDATE registrations SET {columns} WHERE telegram_user_id = ?",
            values,
        )
        conn.commit()


def set_state(user_id: int, state: str) -> None:
    update_registration(user_id, current_state=state)


def get_selected_tools(user_id: int) -> list[str]:
    reg = get_registration(user_id)
    if not reg:
        return []
    raw = reg.get("selected_tools") or "[]"
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return []


def set_selected_tools(user_id: int, tools: list[str]) -> None:
    update_registration(user_id, selected_tools=json.dumps(tools, ensure_ascii=False))


def mark_completed(user_id: int) -> None:
    update_registration(
        user_id,
        is_completed=1,
        current_state="completed",
        registration_date=_now(),
        data_consent=1,
    )


def get_completed_user_ids() -> list[int]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT telegram_user_id FROM registrations WHERE is_completed = 1"
        ).fetchall()
    return [row["telegram_user_id"] for row in rows]


def get_unsynced_registrations() -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT * FROM registrations
            WHERE is_completed = 1 AND synced_to_sheets = 0
            """
        ).fetchall()
    return [dict(row) for row in rows]


def mark_synced(user_id: int) -> None:
    update_registration(user_id, synced_to_sheets=1)


def get_stats() -> dict[str, Any]:
    with get_connection() as conn:
        total = conn.execute(
            "SELECT COUNT(*) AS c FROM registrations WHERE is_completed = 1"
        ).fetchone()["c"]
        llm_rows = conn.execute(
            """
            SELECT llm_experience, COUNT(*) AS c
            FROM registrations
            WHERE is_completed = 1
            GROUP BY llm_experience
            """
        ).fetchall()
        source_rows = conn.execute(
            """
            SELECT traffic_source, COUNT(*) AS c
            FROM registrations
            WHERE is_completed = 1
            GROUP BY traffic_source
            """
        ).fetchall()
    return {
        "total": total,
        "llm_experience": {row["llm_experience"] or "—": row["c"] for row in llm_rows},
        "traffic_source": {row["traffic_source"] or "—": row["c"] for row in source_rows},
    }


def get_all_completed() -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM registrations WHERE is_completed = 1 ORDER BY registration_date"
        ).fetchall()
    return [dict(row) for row in rows]


def save_feedback_link(
    user_id: int,
    user_message_id: int,
    admin_message_id: int,
    admin_chat_id: int,
) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO feedback_links (user_id, user_message_id, admin_message_id, admin_chat_id)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, user_message_id, admin_message_id, admin_chat_id),
        )
        conn.commit()


def get_feedback_by_admin_message(admin_chat_id: int, admin_message_id: int) -> dict[str, Any] | None:
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT * FROM feedback_links
            WHERE admin_chat_id = ? AND admin_message_id = ?
            ORDER BY id DESC LIMIT 1
            """,
            (admin_chat_id, admin_message_id),
        ).fetchone()
    return dict(row) if row else None


def is_broadcast_sent(broadcast_id: str) -> bool:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT 1 FROM scheduled_broadcast_log WHERE broadcast_id = ?",
            (broadcast_id,),
        ).fetchone()
    return row is not None


def mark_broadcast_sent(broadcast_id: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO scheduled_broadcast_log (broadcast_id) VALUES (?)",
            (broadcast_id,),
        )
        conn.commit()


def get_segment_user_ids(segment: str) -> list[int]:
    query = "SELECT telegram_user_id FROM registrations WHERE is_completed = 1"
    params: list[Any] = []
    if segment == "llm_production":
        query += " AND llm_experience = ?"
        params.append("production")
    elif segment == "developers":
        query += " AND occupation = ?"
        params.append("developer")
    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
    return [row["telegram_user_id"] for row in rows]
