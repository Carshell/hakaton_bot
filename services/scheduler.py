import logging
from datetime import datetime, timezone

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import SCHEDULED_BROADCASTS
from database import get_completed_user_ids, is_broadcast_sent, mark_broadcast_sent
from services.broadcast import send_broadcast
from services.google_sheets import backfill_unsynced

logger = logging.getLogger(__name__)


def setup_scheduler(bot: Bot) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone="UTC")

    async def hourly_backfill() -> None:
        count = await backfill_unsynced()
        if count:
            logger.info("Backfilled %s registrations to Google Sheets", count)

    scheduler.add_job(hourly_backfill, "interval", hours=1, id="sheets_backfill")

    for item in SCHEDULED_BROADCASTS:
        broadcast_id = item["id"]
        run_at: datetime = item["run_at"]
        if run_at.tzinfo is None:
            run_at = run_at.replace(tzinfo=timezone.utc)

        async def scheduled_push(bid: str = broadcast_id, text: str = item["text"]) -> None:
            if is_broadcast_sent(bid):
                return
            user_ids = get_completed_user_ids()
            await send_broadcast(bot, user_ids, text)
            mark_broadcast_sent(bid)
            logger.info("Scheduled broadcast %s sent to %s users", bid, len(user_ids))

        scheduler.add_job(
            scheduled_push,
            "date",
            run_date=run_at,
            id=broadcast_id,
            replace_existing=True,
        )

    return scheduler
