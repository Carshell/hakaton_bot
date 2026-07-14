import json

from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.keyboards import (
    confirmation_kb,
    consent_kb,
    consent_text,
    details_kb,
    edit_fields_kb,
    format_registration_card,
    llm_kb,
    role_kb,
    skip_kb,
    source_kb,
    telegram_confirm_kb,
    tools_kb,
    welcome_kb,
    workplace_kb,
)
from bot.states import RegistrationStates
from bot.texts import (
    DETAILS_TEXT,
    EMAIL_ERROR,
    EMAIL_PROMPT,
    NAME_ERROR,
    NAME_PROMPT,
    PROJECT_ERROR,
    PROJECT_PROMPT,
    ROLE_OTHER_PROMPT,
    ROLE_PROMPT,
    SOCIAL_ERROR,
    SOCIAL_PROMPT,
    SOURCE_OTHER_PROMPT,
    SOURCE_PROMPT,
    TELEGRAM_CONFIRM,
    TELEGRAM_ERROR,
    TELEGRAM_PROMPT,
    TOOLS_PROMPT,
    WELCOME_TEXT,
    WORKPLACE_OTHER_PROMPT,
    WORKPLACE_PROMPT,
    WORKS_ERROR,
    WORKS_PROMPT,
    LLM_PROMPT,
)
from bot.validators import (
    normalize_telegram_username,
    validate_email,
    validate_full_name,
    validate_portfolio,
    validate_project,
    validate_telegram_username,
    validate_url,
)
from database import (
    get_registration,
    get_selected_tools,
    set_selected_tools,
    set_state,
    update_registration,
)


def _uid(message: Message, user_id: int | None) -> int:
    return user_id if user_id is not None else message.from_user.id


STATE_MAP = {
    "welcome": RegistrationStates.welcome,
    "details": RegistrationStates.details,
    "name": RegistrationStates.name,
    "email": RegistrationStates.email,
    "telegram_username": RegistrationStates.telegram_username,
    "social": RegistrationStates.social,
    "works": RegistrationStates.works,
    "role": RegistrationStates.role,
    "role_other": RegistrationStates.role_other,
    "workplace": RegistrationStates.workplace,
    "workplace_other": RegistrationStates.workplace_other,
    "llm_exp": RegistrationStates.llm_exp,
    "tools": RegistrationStates.tools,
    "project": RegistrationStates.project,
    "source": RegistrationStates.source,
    "source_other": RegistrationStates.source_other,
    "consent": RegistrationStates.consent,
    "confirmation": RegistrationStates.confirmation,
}

EDIT_FIELD_STATE = {
    "full_name": RegistrationStates.name,
    "email": RegistrationStates.email,
    "telegram_username": RegistrationStates.telegram_username,
    "social_media": RegistrationStates.social,
    "portfolio_links": RegistrationStates.works,
    "occupation": RegistrationStates.role,
    "workplace": RegistrationStates.workplace,
    "llm_experience": RegistrationStates.llm_exp,
    "tools": RegistrationStates.tools,
    "coolest_project": RegistrationStates.project,
    "traffic_source": RegistrationStates.source,
}


async def show_welcome(message: Message, state: FSMContext, user_id: int | None = None) -> None:
    uid = _uid(message, user_id)
    await state.set_state(RegistrationStates.welcome)
    set_state(uid, "welcome")
    await message.answer(WELCOME_TEXT, reply_markup=welcome_kb(), parse_mode="HTML")


async def show_details(message: Message, state: FSMContext, user_id: int | None = None) -> None:
    uid = _uid(message, user_id)
    await state.set_state(RegistrationStates.details)
    set_state(uid, "details")
    await message.answer(DETAILS_TEXT, reply_markup=details_kb())


async def show_name(message: Message, state: FSMContext, user_id: int | None = None) -> None:
    uid = _uid(message, user_id)
    await state.set_state(RegistrationStates.name)
    set_state(uid, "name")
    await message.answer(NAME_PROMPT)


async def show_email(message: Message, state: FSMContext, user_id: int | None = None) -> None:
    uid = _uid(message, user_id)
    await state.set_state(RegistrationStates.email)
    set_state(uid, "email")
    await message.answer(EMAIL_PROMPT)


async def show_telegram(
    message: Message,
    state: FSMContext,
    username: str | None,
    user_id: int | None = None,
) -> None:
    uid = _uid(message, user_id)
    await state.set_state(RegistrationStates.telegram_username)
    set_state(uid, "telegram_username")
    if username:
        update_registration(
            uid,
            telegram_username=normalize_telegram_username(username),
        )
        await message.answer(
            TELEGRAM_CONFIRM.format(username=normalize_telegram_username(username)),
            reply_markup=telegram_confirm_kb(),
        )
    else:
        await message.answer(TELEGRAM_PROMPT)


async def show_social(message: Message, state: FSMContext, user_id: int | None = None) -> None:
    uid = _uid(message, user_id)
    await state.set_state(RegistrationStates.social)
    set_state(uid, "social")
    await message.answer(SOCIAL_PROMPT, reply_markup=skip_kb())


async def show_works(message: Message, state: FSMContext, user_id: int | None = None) -> None:
    uid = _uid(message, user_id)
    await state.set_state(RegistrationStates.works)
    set_state(uid, "works")
    await message.answer(WORKS_PROMPT, reply_markup=skip_kb("reg:skip_works"))


async def show_role(message: Message, state: FSMContext, user_id: int | None = None) -> None:
    uid = _uid(message, user_id)
    await state.set_state(RegistrationStates.role)
    set_state(uid, "role")
    await message.answer(ROLE_PROMPT, reply_markup=role_kb())


async def show_workplace(message: Message, state: FSMContext, user_id: int | None = None) -> None:
    uid = _uid(message, user_id)
    await state.set_state(RegistrationStates.workplace)
    set_state(uid, "workplace")
    await message.answer(WORKPLACE_PROMPT, reply_markup=workplace_kb())


async def show_llm(message: Message, state: FSMContext, user_id: int | None = None) -> None:
    uid = _uid(message, user_id)
    await state.set_state(RegistrationStates.llm_exp)
    set_state(uid, "llm_exp")
    await message.answer(LLM_PROMPT, reply_markup=llm_kb())


async def show_tools(message: Message, state: FSMContext, user_id: int | None = None) -> None:
    uid = _uid(message, user_id)
    await state.set_state(RegistrationStates.tools)
    set_state(uid, "tools")
    selected = get_selected_tools(uid)
    await message.answer(TOOLS_PROMPT, reply_markup=tools_kb(selected))


async def show_project(message: Message, state: FSMContext, user_id: int | None = None) -> None:
    uid = _uid(message, user_id)
    await state.set_state(RegistrationStates.project)
    set_state(uid, "project")
    await message.answer(PROJECT_PROMPT)


async def show_source(message: Message, state: FSMContext, user_id: int | None = None) -> None:
    uid = _uid(message, user_id)
    reg = get_registration(uid)
    if reg and reg.get("start_payload"):
        await show_consent(message, state, user_id=uid)
        return
    await state.set_state(RegistrationStates.source)
    set_state(uid, "source")
    await message.answer(SOURCE_PROMPT, reply_markup=source_kb())


async def show_consent(message: Message, state: FSMContext, user_id: int | None = None) -> None:
    uid = _uid(message, user_id)
    await state.set_state(RegistrationStates.consent)
    set_state(uid, "consent")
    await message.answer(consent_text(), reply_markup=consent_kb(), parse_mode="HTML")


async def show_confirmation(message: Message, state: FSMContext, user_id: int | None = None) -> None:
    uid = _uid(message, user_id)
    await state.set_state(RegistrationStates.confirmation)
    set_state(uid, "confirmation")
    update_registration(uid, editing_field=None)
    reg = get_registration(uid)
    await message.answer(
        format_registration_card(reg or {}),
        reply_markup=confirmation_kb(),
        parse_mode="HTML",
    )


async def show_edit_menu(message: Message, state: FSMContext) -> None:
    await message.answer("Обери поле для редагування:", reply_markup=edit_fields_kb())


async def resume_state(
    message: Message,
    state: FSMContext,
    reg: dict,
    user_id: int | None = None,
) -> None:
    uid = user_id or reg.get("telegram_user_id") or message.from_user.id
    current = reg.get("current_state") or "welcome"
    fsm_state = STATE_MAP.get(current, RegistrationStates.welcome)
    await state.set_state(fsm_state)

    dispatch = {
        "welcome": show_welcome,
        "details": show_details,
        "name": show_name,
        "email": show_email,
        "social": show_social,
        "works": show_works,
        "role": show_role,
        "role_other": lambda m, s: m.answer(ROLE_OTHER_PROMPT),
        "workplace": show_workplace,
        "workplace_other": lambda m, s: m.answer(WORKPLACE_OTHER_PROMPT),
        "llm_exp": show_llm,
        "tools": show_tools,
        "project": show_project,
        "source": show_source,
        "source_other": lambda m, s: m.answer(SOURCE_OTHER_PROMPT),
        "consent": show_consent,
        "confirmation": show_confirmation,
    }

    if current == "telegram_username":
        await show_telegram(message, state, reg.get("telegram_username"), user_id=uid)
        return

    handler = dispatch.get(current, show_welcome)
    if current in {"role_other", "workplace_other", "source_other"}:
        await handler(message, state)
    else:
        await handler(message, state, user_id=uid)


async def after_field_update(
    message: Message,
    state: FSMContext,
    user_id: int,
    completed_step: str,
    telegram_username: str | None = None,
) -> None:
    reg = get_registration(user_id)
    if reg and reg.get("editing_field"):
        await show_confirmation(message, state, user_id=user_id)
        return

    flow = {
        "name": show_email,
        "telegram_username": show_social,
        "social": show_works,
        "works": show_role,
        "role": show_workplace,
        "role_other": show_workplace,
        "workplace": show_llm,
        "workplace_other": show_llm,
        "llm_exp": show_tools,
        "tools": show_project,
        "project": show_source,
        "source": show_consent,
        "source_other": show_consent,
    }
    if completed_step == "email":
        username = telegram_username
        if username is None and message.from_user.id == user_id:
            username = message.from_user.username
        await show_telegram(message, state, username, user_id=user_id)
        return

    next_step = flow.get(completed_step)
    if next_step:
        await next_step(message, state, user_id=user_id)


async def handle_name_input(message: Message, state: FSMContext) -> bool:
    if not validate_full_name(message.text or ""):
        await message.answer(NAME_ERROR)
        return False
    update_registration(message.from_user.id, full_name=message.text.strip())
    await after_field_update(message, state, message.from_user.id, "name")
    return True


async def handle_email_input(message: Message, state: FSMContext) -> bool:
    if not validate_email(message.text or ""):
        await message.answer(EMAIL_ERROR)
        return False
    update_registration(message.from_user.id, email=message.text.strip())
    await after_field_update(
        message,
        state,
        message.from_user.id,
        "email",
        telegram_username=message.from_user.username,
    )
    return True


async def handle_telegram_input(message: Message, state: FSMContext) -> bool:
    if not validate_telegram_username(message.text or ""):
        await message.answer(TELEGRAM_ERROR)
        return False
    update_registration(
        message.from_user.id,
        telegram_username=normalize_telegram_username(message.text or ""),
    )
    await after_field_update(message, state, message.from_user.id, "telegram_username")
    return True


async def handle_social_input(message: Message, state: FSMContext) -> bool:
    if not validate_url(message.text or ""):
        await message.answer(SOCIAL_ERROR)
        return False
    update_registration(message.from_user.id, social_media=message.text.strip())
    await after_field_update(message, state, message.from_user.id, "social")
    return True


async def handle_works_input(message: Message, state: FSMContext) -> bool:
    if not validate_portfolio(message.text or ""):
        await message.answer(WORKS_ERROR)
        return False
    update_registration(message.from_user.id, portfolio_links=message.text.strip())
    await after_field_update(message, state, message.from_user.id, "works")
    return True


async def handle_project_input(message: Message, state: FSMContext) -> bool:
    if not validate_project(message.text or ""):
        await message.answer(PROJECT_ERROR)
        return False
    update_registration(message.from_user.id, coolest_project=message.text.strip())
    await after_field_update(message, state, message.from_user.id, "project")
    return True


async def handle_other_text(message: Message, state: FSMContext, field: str) -> bool:
    value = (message.text or "").strip()
    if len(value) < 2:
        await message.answer("Напиши трохи детальніше.")
        return False
    step_map = {
        "occupation": "role_other",
        "workplace": "workplace_other",
        "traffic_source": "source_other",
    }
    update_registration(message.from_user.id, **{field: value})
    await after_field_update(
        message, state, message.from_user.id, step_map.get(field, field)
    )
    return True


async def save_tools_and_continue(message: Message, state: FSMContext, user_id: int) -> None:
    selected = get_selected_tools(user_id)
    update_registration(user_id, tools=json.dumps(selected, ensure_ascii=False))
    await after_field_update(message, state, user_id, "tools")
