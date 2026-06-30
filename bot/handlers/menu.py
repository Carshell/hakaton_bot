from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards import faq_answer_kb, faq_kb, main_menu_kb
from bot.states import MenuStates
from bot.texts import FEEDBACK_PROMPT
from config import FAQ_ITEMS, MENTORS_AND_JURY, SCHEDULE_TEXT, TECH_TASK_TEXT

router = Router()


async def send_main_menu(message: Message) -> None:
    await message.answer("📋 <b>Головне меню</b>", reply_markup=main_menu_kb())


@router.message(Command("menu"))
async def cmd_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await send_main_menu(message)


@router.callback_query(F.data == "menu:main")
async def on_main_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.clear()
    await callback.message.answer("📋 <b>Головне меню</b>", reply_markup=main_menu_kb())


@router.callback_query(F.data == "menu:schedule")
async def on_schedule(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.answer(SCHEDULE_TEXT, reply_markup=main_menu_kb())


@router.callback_query(F.data == "menu:tech")
async def on_tech(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.answer(TECH_TASK_TEXT, reply_markup=main_menu_kb())


@router.callback_query(F.data == "menu:mentors")
async def on_mentors(callback: CallbackQuery) -> None:
    await callback.answer()
    text = "👥 <b>Ментори і журі</b>\n\n" + "\n".join(f"• {name}" for name in MENTORS_AND_JURY)
    await callback.message.answer(text, reply_markup=main_menu_kb())


@router.callback_query(F.data == "menu:faq")
async def on_faq(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.answer("❓ <b>FAQ</b>\n\nОбери питання:", reply_markup=faq_kb())


@router.callback_query(F.data.startswith("faq:"))
async def on_faq_item(callback: CallbackQuery) -> None:
    await callback.answer()
    index = int(callback.data.split(":")[1])
    question, answer = FAQ_ITEMS[index]
    text = f"<b>{question}</b>\n\n{answer}"
    await callback.message.edit_text(text, reply_markup=faq_answer_kb(index))


@router.callback_query(F.data == "menu:feedback")
async def on_feedback(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.set_state(MenuStates.feedback)
    await callback.message.answer(FEEDBACK_PROMPT)
