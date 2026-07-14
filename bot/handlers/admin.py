import csv
import io
import logging
from typing import Any

from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from bot.admins import get_admin_ids
from bot.keyboards import broadcast_confirm_kb
from bot.states import AdminStates
from database import get_all_completed, get_completed_user_ids, get_segment_user_ids, get_stats
from services.broadcast import send_broadcast

logger = logging.getLogger(__name__)
router = Router()


def _is_admin(user_id: int) -> bool:
    return user_id in get_admin_ids()


@router.message(Command("stats"))
async def cmd_stats(message: Message) -> None:
    if not _is_admin(message.from_user.id):
        return

    stats = get_stats()
    llm_lines = "\n".join(f"  • {k}: {v}" for k, v in stats["llm_experience"].items()) or "  —"
    source_lines = "\n".join(f"  • {k}: {v}" for k, v in stats["traffic_source"].items()) or "  —"
    text = (
        f"📊 <b>Статистика реєстрацій</b>\n\n"
        f"Всього: <b>{stats['total']}</b>\n\n"
        f"<b>LLM досвід:</b>\n{llm_lines}\n\n"
        f"<b>Джерела трафіку:</b>\n{source_lines}"
    )
    await message.answer(text)


@router.message(Command("export"))
async def cmd_export(message: Message) -> None:
    if not _is_admin(message.from_user.id):
        return

    rows = get_all_completed()
    output = io.StringIO()
    fieldnames = [
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
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow({key: row.get(key, "") for key in fieldnames})

    file = BufferedInputFile(
        output.getvalue().encode("utf-8-sig"),
        filename="registrations.csv",
    )
    await message.answer_document(file, caption="Експорт реєстрацій")


@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message, state: FSMContext) -> None:
    if not _is_admin(message.from_user.id):
        return

    await state.set_state(AdminStates.broadcast_text)
    await message.answer("Надішли текст розсилки:")


@router.message(Command("broadcast_segment"))
async def cmd_broadcast_segment(message: Message, command: CommandObject, state: FSMContext) -> None:
    if not _is_admin(message.from_user.id):
        return

    segment = (command.args or "").strip()
    if not segment:
        await message.answer(
            "Використання: /broadcast_segment <сегмент>\n"
            "Доступні: llm_production, developers"
        )
        return

    user_ids = get_segment_user_ids(segment)
    await state.update_data(
        broadcast_text=None,
        broadcast_segment=segment,
        broadcast_user_ids=user_ids,
    )
    await state.set_state(AdminStates.broadcast_text)
    await message.answer(
        f"Сегмент <b>{segment}</b>: {len(user_ids)} отримувачів.\n"
        "Надішли текст розсилки:"
    )


@router.message(AdminStates.broadcast_text)
async def on_broadcast_text(message: Message, state: FSMContext) -> None:
    if not _is_admin(message.from_user.id):
        return

    data = await state.get_data()
    user_ids = data.get("broadcast_user_ids") or get_completed_user_ids()
    text = message.text or ""
    await state.update_data(broadcast_text=text, broadcast_user_ids=user_ids)
    await state.set_state(AdminStates.broadcast_confirm)
    await message.answer(
        f"<b>Прев'ю розсилки</b> ({len(user_ids)} отримувачів):\n\n{text}",
        reply_markup=broadcast_confirm_kb(),
    )


@router.callback_query(F.data == "admin:broadcast_cancel")
async def on_broadcast_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    if not _is_admin(callback.from_user.id):
        return
    await callback.answer()
    await state.clear()
    await callback.message.answer("Розсилку скасовано.")


@router.callback_query(F.data == "admin:broadcast_send")
async def on_broadcast_send(callback: CallbackQuery, state: FSMContext) -> None:
    if not _is_admin(callback.from_user.id):
        return
    await callback.answer()
    data = await state.get_data()
    text = data.get("broadcast_text", "")
    user_ids = data.get("broadcast_user_ids") or get_completed_user_ids()
    await state.clear()
    await callback.message.answer(f"Розсилка запущена для {len(user_ids)} користувачів...")
    sent, failed = await send_broadcast(callback.bot, user_ids, text)
    await callback.message.answer(f"Готово. Надіслано: {sent}, помилок: {failed}.")
