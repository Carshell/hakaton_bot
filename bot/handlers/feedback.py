import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.admins import get_admin_ids
from bot.states import MenuStates
from bot.texts import FEEDBACK_SENT
from database import get_feedback_by_admin_message, save_feedback_link

logger = logging.getLogger(__name__)
router = Router()


@router.message(MenuStates.feedback)
async def on_feedback_message(message: Message, state: FSMContext) -> None:
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


@router.message(F.reply_to_message)
async def on_admin_reply(message: Message) -> None:
    admin_ids = get_admin_ids()
    if message.from_user.id not in admin_ids:
        return

    link = get_feedback_by_admin_message(
        message.chat.id,
        message.reply_to_message.message_id,
    )
    if not link:
        return

    reply_text = message.text or message.caption or ""
    if not reply_text:
        await message.answer("Надішли текстову відповідь.")
        return

    await message.bot.send_message(
        chat_id=link["user_id"],
        text=f"📩 Відповідь від організаторів:\n\n{reply_text}",
    )
    await message.answer("✅ Відповідь надіслано користувачу.")
