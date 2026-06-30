import asyncio
import logging
import os

from dotenv import load_dotenv

load_dotenv()

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.handlers import get_routers
from bot.handlers.fallback import router as fallback_router
from database import init_db
from services.scheduler import setup_scheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main() -> None:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN is not set in environment or .env file")

    init_db()

    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    for router in get_routers():
        dp.include_router(router)
    dp.include_router(fallback_router)

    await bot.delete_webhook(drop_pending_updates=True)

    scheduler = setup_scheduler(bot)
    scheduler.start()

    try:
        logger.info("Bot started")
        await dp.start_polling(bot)
    finally:
        scheduler.shutdown(wait=False)


if __name__ == "__main__":
    asyncio.run(main())
