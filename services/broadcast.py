import asyncio
import logging
import os
from typing import Any

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError

from config import BROADCAST_RATE_LIMIT

logger = logging.getLogger(__name__)


async def send_broadcast(bot: Bot, user_ids: list[int], text: str) -> tuple[int, int]:
    if not user_ids:
        return 0, 0

    delay = 1 / BROADCAST_RATE_LIMIT
    sent = 0
    failed = 0

    for user_id in user_ids:
        try:
            await bot.send_message(chat_id=user_id, text=text)
            sent += 1
        except TelegramAPIError as exc:
            failed += 1
            logger.warning("Broadcast failed for %s: %s", user_id, exc)
        await asyncio.sleep(delay)

    return sent, failed
