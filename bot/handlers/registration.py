import logging

from aiogram import F, Router
from aiogram.filters import CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.filters import RegistrationTextFilter
from bot.keyboards import main_menu_kb
from bot.registration_flow import (
    EDIT_FIELD_STATE,
    STATE_MAP,
    handle_email_input,
    handle_name_input,
    handle_other_text,
    handle_project_input,
    handle_social_input,
    handle_telegram_input,
    handle_works_input,
    resume_state,
    show_confirmation,
    show_consent,
    show_details,
    show_edit_menu,
    show_name,
    show_source,
    show_telegram,
    show_welcome,
)
from bot.states import RegistrationStates
from bot.texts import CONSENT_DENIED, REGISTRATION_COMPLETE, RESUME_PROMPT, UNKNOWN_INPUT
from database import (
    create_registration,
    ensure_registration,
    get_registration,
    mark_completed,
    set_state,
    update_registration,
)
from services.google_sheets import sync_registration

logger = logging.getLogger(__name__)
router = Router()

TEXT_HANDLERS = {
    "name": handle_name_input,
    "email": handle_email_input,
    "telegram_username": handle_telegram_input,
    "social": handle_social_input,
    "works": handle_works_input,
    "role_other": lambda m, s: handle_other_text(m, s, "occupation"),
    "workplace_other": lambda m, s: handle_other_text(m, s, "workplace"),
    "project": handle_project_input,
    "source_other": lambda m, s: handle_other_text(m, s, "traffic_source"),
}


@router.message(RegistrationTextFilter())
async def on_registration_text(
    message: Message,
    state: FSMContext,
    reg_state: str,
) -> None:
    fsm_state = STATE_MAP.get(reg_state)
    if fsm_state:
        await state.set_state(fsm_state)
    handler = TEXT_HANDLERS.get(reg_state)
    if handler:
        await handler(message, state)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, command: CommandObject) -> None:
    user_id = message.from_user.id
    payload = command.args

    reg = get_registration(user_id)
    if reg and reg.get("is_completed"):
        await state.clear()
        await message.answer(
            "Ти вже зареєстрований! Ось головне меню:",
            reply_markup=main_menu_kb(),
        )
        return

    if reg and reg.get("current_state") not in (None, "welcome", "completed"):
        from bot.keyboards import resume_kb

        await message.answer(RESUME_PROMPT, reply_markup=resume_kb())
        return

    create_registration(user_id, start_payload=payload)
    if payload:
        update_registration(user_id, traffic_source=payload)
    await show_welcome(message, state)


@router.callback_query(F.data == "reg:details")
async def on_details(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await show_details(callback.message, state, user_id=callback.from_user.id)


@router.callback_query(F.data == "reg:start")
async def on_reg_start(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    ensure_registration(callback.from_user.id)
    await show_name(callback.message, state, user_id=callback.from_user.id)


@router.callback_query(F.data == "reg:resume")
async def on_resume(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    reg = get_registration(callback.from_user.id)
    if reg:
        await resume_state(callback.message, state, reg, user_id=callback.from_user.id)


@router.callback_query(F.data == "reg:restart")
async def on_restart(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    reg = get_registration(callback.from_user.id)
    payload = reg.get("start_payload") if reg else None
    create_registration(callback.from_user.id, start_payload=payload)
    await show_welcome(callback.message, state, user_id=callback.from_user.id)


@router.callback_query(F.data == "reg:confirm_tg")
async def on_confirm_tg(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    from bot.registration_flow import after_field_update

    set_state(callback.from_user.id, "telegram_username")
    await after_field_update(
        callback.message, state, callback.from_user.id, "telegram_username"
    )


@router.callback_query(F.data == "reg:change_tg")
async def on_change_tg(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await show_telegram(callback.message, state, username=None, user_id=callback.from_user.id)


@router.callback_query(F.data == "reg:skip_social")
async def on_skip_social(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    update_registration(callback.from_user.id, social_media=None)
    from bot.registration_flow import show_works

    await show_works(callback.message, state, user_id=callback.from_user.id)


@router.callback_query(F.data.startswith("reg:role:"))
async def on_role(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    value = callback.data.split(":")[-1]
    if value == "other":
        await state.set_state(RegistrationStates.role_other)
        set_state(callback.from_user.id, "role_other")
        from bot.texts import ROLE_OTHER_PROMPT

        await callback.message.answer(ROLE_OTHER_PROMPT)
        return
    update_registration(callback.from_user.id, occupation=value)
    from bot.registration_flow import after_field_update

    set_state(callback.from_user.id, "role")
    await after_field_update(callback.message, state, callback.from_user.id, "role")


@router.callback_query(F.data.startswith("reg:workplace:"))
async def on_workplace(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    value = callback.data.split(":")[-1]
    if value == "other":
        await state.set_state(RegistrationStates.workplace_other)
        set_state(callback.from_user.id, "workplace_other")
        from bot.texts import WORKPLACE_OTHER_PROMPT

        await callback.message.answer(WORKPLACE_OTHER_PROMPT)
        return
    update_registration(callback.from_user.id, workplace=value)
    set_state(callback.from_user.id, "workplace")
    from bot.registration_flow import after_field_update

    await after_field_update(callback.message, state, callback.from_user.id, "workplace")


@router.callback_query(F.data.startswith("reg:llm:"))
async def on_llm(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    value = callback.data.split(":")[-1]
    update_registration(callback.from_user.id, llm_experience=value)
    set_state(callback.from_user.id, "llm_exp")
    from bot.registration_flow import after_field_update

    await after_field_update(callback.message, state, callback.from_user.id, "llm_exp")


@router.callback_query(F.data.startswith("reg:tool:"))
async def on_tool_toggle(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    tool = callback.data.split(":", 2)[-1]
    from database import get_selected_tools, set_selected_tools
    from bot.keyboards import tools_kb

    selected = get_selected_tools(callback.from_user.id)
    if tool in selected:
        selected.remove(tool)
    else:
        selected.append(tool)
    set_selected_tools(callback.from_user.id, selected)
    await callback.message.edit_reply_markup(reply_markup=tools_kb(selected))


@router.callback_query(F.data == "reg:tools_done")
async def on_tools_done(callback: CallbackQuery, state: FSMContext) -> None:
    from database import get_selected_tools
    from bot.registration_flow import save_tools_and_continue

    selected = get_selected_tools(callback.from_user.id)
    if not selected:
        await callback.answer("Обери хоча б один інструмент.", show_alert=True)
        return
    await callback.answer()
    await save_tools_and_continue(callback.message, state, callback.from_user.id)


@router.callback_query(F.data.startswith("reg:source:"))
async def on_source(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    value = callback.data.split(":")[-1]
    if value == "other":
        await state.set_state(RegistrationStates.source_other)
        set_state(callback.from_user.id, "source_other")
        from bot.texts import SOURCE_OTHER_PROMPT

        await callback.message.answer(SOURCE_OTHER_PROMPT)
        return
    update_registration(callback.from_user.id, traffic_source=value)
    set_state(callback.from_user.id, "source")
    await show_consent(callback.message, state, user_id=callback.from_user.id)


@router.callback_query(F.data == "reg:consent_yes")
async def on_consent_yes(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    update_registration(callback.from_user.id, data_consent=1)
    await show_confirmation(callback.message, state, user_id=callback.from_user.id)


@router.callback_query(F.data == "reg:consent_no")
async def on_consent_no(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.clear()
    await callback.message.answer(CONSENT_DENIED)


@router.callback_query(F.data == "reg:edit_menu")
async def on_edit_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await show_edit_menu(callback.message, state)


@router.callback_query(F.data == "reg:edit_back")
async def on_edit_back(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await show_confirmation(callback.message, state, user_id=callback.from_user.id)


@router.callback_query(F.data.startswith("reg:edit:"))
async def on_edit_field(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    field = callback.data.split(":")[-1]
    update_registration(callback.from_user.id, editing_field=field)
    target_state = EDIT_FIELD_STATE.get(field)
    if not target_state:
        return
    await state.set_state(target_state)
    set_state(callback.from_user.id, field if field != "social_media" else "social")

    prompts = {
        "full_name": ("name", "Напиши своє ім'я та прізвище:"),
        "email": ("email", "Твій email:"),
        "telegram_username": ("telegram_username", "Твій Telegram-нік:"),
        "social_media": ("social", "Посилання на соцмережу:"),
        "portfolio_links": ("works", "Посилання на роботи:"),
        "occupation": ("role", None),
        "workplace": ("workplace", None),
        "llm_experience": ("llm_exp", None),
        "tools": ("tools", None),
        "coolest_project": ("project", "Опиши свій AI-проєкт:"),
        "traffic_source": ("source", None),
    }
    key, text = prompts.get(field, (field, "Введи нове значення:"))
    set_state(callback.from_user.id, key)
    if field == "occupation":
        from bot.registration_flow import show_role

        await show_role(callback.message, state, user_id=callback.from_user.id)
    elif field == "workplace":
        from bot.registration_flow import show_workplace

        await show_workplace(callback.message, state, user_id=callback.from_user.id)
    elif field == "llm_experience":
        from bot.registration_flow import show_llm

        await show_llm(callback.message, state, user_id=callback.from_user.id)
    elif field == "tools":
        from bot.registration_flow import show_tools

        await show_tools(callback.message, state, user_id=callback.from_user.id)
    elif field == "traffic_source":
        await show_source(callback.message, state, user_id=callback.from_user.id)
    elif text:
        await callback.message.answer(text)


@router.callback_query(F.data == "reg:submit")
async def on_submit(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    user_id = callback.from_user.id
    mark_completed(user_id)
    try:
        await sync_registration(user_id)
    except Exception:
        logger.exception("Google Sheets sync failed for user %s", user_id)

    await state.clear()
    await callback.message.answer(REGISTRATION_COMPLETE, reply_markup=main_menu_kb(), parse_mode="HTML")


@router.message(
    RegistrationStates.welcome,
    RegistrationStates.details,
    RegistrationStates.role,
    RegistrationStates.workplace,
    RegistrationStates.llm_exp,
    RegistrationStates.tools,
    RegistrationStates.source,
    RegistrationStates.consent,
    RegistrationStates.confirmation,
)
async def on_invalid_registration_input(message: Message) -> None:
    await message.answer(UNKNOWN_INPUT)
