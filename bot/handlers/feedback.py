import os

from aiogram import F, Router
from aiogram.types import Message

from bot.states import MenuStates
from bot.texts import FEEDBACK_SENT
from database import save_feedback_link

router = Router()

ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")


@router.message(MenuStates.feedback)
async def on_feedback_message(message: Message) -> None:
    if not ADMIN_CHAT_ID:
        await message.answer("Зворотний зв'язок тимчасово недоступний.")
        return

    admin_chat_id = int(ADMIN_CHAT_ID)
    user = message.from_user
    header = (
        f"💬 Повідомлення від @{user.username or 'user'} "
        f"(id: {user.id})\n"
        f"---\n"
    )
    forwarded = await message.bot.send_message(
        chat_id=admin_chat_id,
        text=header + (message.text or message.caption or "[медіа]"),
    )
    save_feedback_link(
        user_id=user.id,
        user_message_id=message.message_id,
        admin_message_id=forwarded.message_id,
        admin_chat_id=admin_chat_id,
    )
    await message.answer(FEEDBACK_SENT)


@router.message(F.reply_to_message)
async def on_admin_reply(message: Message) -> None:
    if not ADMIN_CHAT_ID:
        return

    admin_ids = {
        int(uid.strip())
        for uid in os.getenv("ADMIN_USER_IDS", "").split(",")
        if uid.strip().isdigit()
    }
    if message.from_user.id not in admin_ids:
        return
    if message.chat.id != int(ADMIN_CHAT_ID):
        return

    from database import get_feedback_by_admin_message

    link = get_feedback_by_admin_message(
        message.chat.id,
        message.reply_to_message.message_id,
    )
    if not link:
        return

    await message.bot.send_message(
        chat_id=link["user_id"],
        text=f"📩 Відповідь від організаторів:\n\n{message.text or message.caption or ''}",
    )
