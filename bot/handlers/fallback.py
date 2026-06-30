from aiogram import Router
from aiogram.types import Message

from bot.texts import UNKNOWN_INPUT

router = Router()


@router.message()
async def on_unknown_message(message: Message) -> None:
    await message.answer(UNKNOWN_INPUT)
