import asyncio
import logging

from dotenv import load_dotenv

from database import init_db
from services.google_sheets import backfill_unsynced

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main() -> None:
    init_db()
    count = await backfill_unsynced()
    logger.info("Backfill complete: %s rows synced", count)


if __name__ == "__main__":
    asyncio.run(main())
