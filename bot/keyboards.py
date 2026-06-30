import json
from typing import Any

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.texts import FIELD_LABELS, LLM_LABELS, ROLE_LABELS, SOURCE_LABELS, TOOL_OPTIONS, WORKPLACE_LABELS
from config import HACKATHON_SITE_URL, LANDING_URL, PRIVACY_POLICY_URL


def welcome_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🚀 Так, поїхали", callback_data="reg:start")
    builder.button(text="📖 Розкажи детальніше", callback_data="reg:details")
    builder.adjust(1)
    return builder.as_markup()


def details_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🚀 Так, поїхали", callback_data="reg:start")
    builder.button(text="🌐 Детальніше", url=LANDING_URL)
    builder.adjust(1)
    return builder.as_markup()


def skip_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="⏭ Пропустити", callback_data="reg:skip_social")
    return builder.as_markup()


def telegram_confirm_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Так", callback_data="reg:confirm_tg")
    builder.button(text="✏️ Інший нік", callback_data="reg:change_tg")
    builder.adjust(2)
    return builder.as_markup()


def single_choice_kb(options: dict[str, str], prefix: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for key, label in options.items():
        builder.button(text=label, callback_data=f"{prefix}:{key}")
    builder.adjust(1)
    return builder.as_markup()


def role_kb() -> InlineKeyboardMarkup:
    return single_choice_kb(ROLE_LABELS, "reg:role")


def workplace_kb() -> InlineKeyboardMarkup:
    return single_choice_kb(WORKPLACE_LABELS, "reg:workplace")


def llm_kb() -> InlineKeyboardMarkup:
    return single_choice_kb(LLM_LABELS, "reg:llm")


def source_kb() -> InlineKeyboardMarkup:
    return single_choice_kb(SOURCE_LABELS, "reg:source")


def tools_kb(selected: list[str]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for tool in TOOL_OPTIONS:
        mark = "✅ " if tool in selected else ""
        builder.button(text=f"{mark}{tool}", callback_data=f"reg:tool:{tool}")
    builder.button(text="✅ Готово", callback_data="reg:tools_done")
    builder.adjust(2, 2, 2, 1, 1)
    return builder.as_markup()


def consent_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Даю згоду", callback_data="reg:consent_yes")
    builder.button(text="❌ Не даю згоди", callback_data="reg:consent_no")
    builder.adjust(1)
    return builder.as_markup()


def resume_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🔄 Продовжити з місця зупинки", callback_data="reg:resume")
    builder.button(text="🆕 Почати спочатку", callback_data="reg:restart")
    builder.adjust(1)
    return builder.as_markup()


def confirmation_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Так, відправити", callback_data="reg:submit")
    builder.button(text="✏️ Виправити", callback_data="reg:edit_menu")
    builder.adjust(1)
    return builder.as_markup()


def edit_fields_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for field, label in FIELD_LABELS.items():
        builder.button(text=label, callback_data=f"reg:edit:{field}")
    builder.button(text="⬅️ Назад", callback_data="reg:edit_back")
    builder.adjust(2)
    return builder.as_markup()


def main_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📅 Розклад події", callback_data="menu:schedule")
    builder.button(text="💻 Технічне завдання", callback_data="menu:tech")
    builder.button(text="👥 Ментори і журі", callback_data="menu:mentors")
    builder.button(text="❓ FAQ", callback_data="menu:faq")
    builder.button(text="💬 Зв'язатися з нами", callback_data="menu:feedback")
    builder.button(text="🌐 Більше інформації", url=HACKATHON_SITE_URL)
    builder.adjust(1)
    return builder.as_markup()


def faq_kb() -> InlineKeyboardMarkup:
    from config import FAQ_ITEMS

    builder = InlineKeyboardBuilder()
    for index, (question, _) in enumerate(FAQ_ITEMS):
        builder.button(text=question, callback_data=f"faq:{index}")
    builder.adjust(1)
    return builder.as_markup()


def faq_answer_kb(index: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Назад до FAQ", callback_data="menu:faq")
    builder.button(text="⬅️ Головне меню", callback_data="menu:main")
    builder.adjust(1)
    return builder.as_markup()


def broadcast_confirm_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Надіслати", callback_data="admin:broadcast_send")
    builder.button(text="❌ Скасувати", callback_data="admin:broadcast_cancel")
    builder.adjust(2)
    return builder.as_markup()


def format_registration_card(data: dict[str, Any]) -> str:
    tools = data.get("tools") or "—"
    if isinstance(tools, str) and tools.startswith("["):
        try:
            tools = ", ".join(json.loads(tools))
        except json.JSONDecodeError:
            pass

    def label_map(value: str | None, mapping: dict[str, str]) -> str:
        if not value:
            return "—"
        return mapping.get(value, value)

    lines = [
        "<b>Перевір свої дані:</b>",
        f"👤 Ім'я: {data.get('full_name') or '—'}",
        f"📧 Email: {data.get('email') or '—'}",
        f"💬 Telegram: {data.get('telegram_username') or '—'}",
        f"🔗 Соцмережа: {data.get('social_media') or '—'}",
        f"💼 Роботи: {data.get('portfolio_links') or '—'}",
        f"🎯 Спеціалізація: {label_map(data.get('occupation'), ROLE_LABELS)}",
        f"🏢 Робота: {label_map(data.get('workplace'), WORKPLACE_LABELS)}",
        f"🤖 LLM: {label_map(data.get('llm_experience'), LLM_LABELS)}",
        f"🛠 Інструменти: {tools}",
        f"⭐ Проєкт: {data.get('coolest_project') or '—'}",
        f"📣 Джерело: {label_map(data.get('traffic_source'), SOURCE_LABELS)}",
        f"✅ Згода: {'Так' if data.get('data_consent') else 'Ні'}",
    ]
    return "\n".join(lines)


def consent_text() -> str:
    from bot.texts import CONSENT_TEXT

    return CONSENT_TEXT.format(privacy_url=PRIVACY_POLICY_URL)
