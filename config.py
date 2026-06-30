import os
from datetime import datetime

LANDING_URL = os.getenv("LANDING_URL", "https://kozakgroup.com")
HACKATHON_SITE_URL = os.getenv("HACKATHON_SITE_URL", LANDING_URL)
PRIVACY_POLICY_URL = os.getenv("PRIVACY_POLICY_URL", LANDING_URL)

MENTORS_AND_JURY = [
    "Олексій Коваленко — Lead AI Engineer, Kozak Group",
    "Марія Шевченко — Head of Product, e-commerce",
    "Дмитро Бондар — Senior Backend, MCP/ACP integrations",
    "Анна Лисенко — AI Research, LLM agents",
]

SCHEDULE_TEXT = (
    "📅 <b>Розклад Kozak Group Agent Jam</b>\n\n"
    "• <b>1 серпня</b> — старт хакатону, відкриття реєстрації команд\n"
    "• <b>1–3 серпня</b> — основний етап розробки AI-агентів\n"
    "• <b>3 серпня</b> — дедлайн подачі рішень\n"
    "• <b>Після 3 серпня</b> — оцінювання журі та оголошення переможців"
)

TECH_TASK_TEXT = (
    "💻 <b>Технічне завдання</b>\n\n"
    "Будуємо AI-агентів для e-commerce з використанням протоколів "
    "<b>MCP</b>, <b>ACP</b>, <b>UCP</b>, <b>AP2</b>.\n\n"
    "Треки:\n"
    "• Інтеграція агентів з каталогом та checkout\n"
    "• Автоматизація підтримки клієнтів\n"
    "• Аналітика та персоналізація через LLM\n\n"
    "Стек на вибір: Claude API, OpenAI API, LangChain/LangGraph, Python."
)

FAQ_ITEMS = [
    (
        "Хто може брати участь?",
        "Middle+ / Senior Backend та AI інженери. Формат — соло.",
    ),
    (
        "Який призовий фонд?",
        "$5 000 + менторство та API-кредити від партнерів.",
    ),
    (
        "Онлайн чи офлайн?",
        "Повністю онлайн, 1–3 серпня 2026.",
    ),
    (
        "Чи потрібна команда?",
        "Ні, хакатон проходить у форматі solo.",
    ),
    (
        "Що потрібно здати?",
        "Робочий AI-агент, репозиторій з кодом та короткий опис рішення.",
    ),
]

SCHEDULED_BROADCASTS = [
    {
        "id": "reminder_jul18",
        "run_at": datetime(2026, 7, 18, 10, 0, 0),
        "text": (
            "🔔 До старту Kozak Group Agent Jam залишилось 2 тижні!\n"
            "Зареєструйся та підготуй свій стек — $5k фонд чекає."
        ),
    },
    {
        "id": "reminder_jul25",
        "run_at": datetime(2026, 7, 25, 10, 0, 0),
        "text": (
            "⏳ Тиждень до Agent Jam!\n"
            "Перевір /menu — там розклад, ТЗ та FAQ."
        ),
    },
    {
        "id": "reminder_jul31",
        "run_at": datetime(2026, 7, 31, 10, 0, 0),
        "text": (
            "🚀 Завтра старт хакатону!\n"
            "Переконайся, що твоя анкета заповнена — /menu"
        ),
    },
    {
        "id": "reminder_aug2",
        "run_at": datetime(2026, 8, 2, 10, 0, 0),
        "text": (
            "💪 День 2 Agent Jam!\n"
            "Завтра дедлайн — не забудь задеплоїти демо."
        ),
    },
    {
        "id": "reminder_aug4",
        "run_at": datetime(2026, 8, 4, 10, 0, 0),
        "text": (
            "🏁 Дякуємо за участь у Agent Jam!\n"
            "Слідкуй за оголошенням переможців у /menu."
        ),
    },
]

BROADCAST_RATE_LIMIT = 30
