import logging

from aiogram import Router
from aiogram.filters import BaseFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.admins import get_admin_ids
from bot.states import MenuStates
from bot.texts import FEEDBACK_SENT
from database import get_feedback_by_admin_message, save_feedback_link

logger = logging.getLogger(__name__)
router = Router()


class AdminFeedbackReplyFilter(BaseFilter):
    """Match only when an admin replies to a tracked feedback message."""

    async def __call__(self, message: Message) -> bool | dict:
        if not message.reply_to_message or not message.from_user:
            return False
        if message.from_user.id not in get_admin_ids():
            return False
        link = get_feedback_by_admin_message(
            message.chat.id,
            message.reply_to_message.message_id,
        )
        if not link:
            return False
        return {"feedback_link": link}


@router.message(AdminFeedbackReplyFilter())
async def on_admin_reply(message: Message, state: FSMContext, feedback_link: dict) -> None:
    reply_text = message.text or message.caption or ""
    if not reply_text:
        await message.answer("Надішли текстову відповідь.")
        return

    await message.bot.send_message(
        chat_id=feedback_link["user_id"],
        text=f"📩 Відповідь від організаторів:\n\n{reply_text}",
    )
    # Leave feedback mode so next replies keep working as admin answers
    await state.clear()
    await message.answer("✅ Відповідь надіслано користувачу.")


@router.message(MenuStates.feedback)
async def on_feedback_message(message: Message) -> None:
    # Safety: never treat an admin reply-to-feedback as a new user message
    if message.reply_to_message and message.from_user.id in get_admin_ids():
        link = get_feedback_by_admin_message(
            message.chat.id,
            message.reply_to_message.message_id,
        )
        if link:
            reply_text = message.text or message.caption or ""
            if reply_text:
                await message.bot.send_message(
                    chat_id=link["user_id"],
                    text=f"📩 Відповідь від організаторів:\n\n{reply_text}",
                )
                await message.answer("✅ Відповідь надіслано користувачу.")
            return

    admin_ids = get_admin_ids()
    if not admin_ids:
        await message.answer("Зворотний зв'язок тимчасово недоступний.")
        return

    user = message.from_user
    body = message.text or message.caption or "[медіа]"
    header = (
        f"💬 Повідомлення від @{user.username or 'user'} "
        f"(id: <code>{user.id}</code>)\n"
        f"Відповідай <b>Reply</b> на це повідомлення.\n"
        f"---\n"
    )

    sent_any = False
    for admin_id in admin_ids:
        try:
            forwarded = await message.bot.send_message(
                chat_id=admin_id,
                text=header + body,
            )
            save_feedback_link(
                user_id=user.id,
                user_message_id=message.message_id,
                admin_message_id=forwarded.message_id,
                admin_chat_id=admin_id,
            )
            sent_any = True
        except Exception:
            logger.exception("Failed to forward feedback to admin %s", admin_id)

    if not sent_any:
        await message.answer(
            "Не вдалося надіслати повідомлення адміну. Спробуй пізніше."
        )
        return

    await message.answer(FEEDBACK_SENT)
