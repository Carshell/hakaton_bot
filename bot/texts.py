WELCOME_TEXT = (
    "Привіт! Я бот <b>Kozak Group Agent Jam</b>.\n\n"
    "📅 22-25 серпня 2026 | 💻 Онлайн, соло | 💰 $5 000.\n\n"
    "Готовий зареєструватися?"
)

DETAILS_TEXT = (
    "Що будуємо: робочий AI-MVP для e-commerce — "
    "розумний каталог і пошук за запитом покупця.\n\n"
    "Хто потрібен: AI-інженери, які будують робочі рішення.\n\n"
    "Призовий фонд — $5k на трьох переможців:\n"
    "🥇 1 місце — $3 000\n"
    "🥈 2 місце — $1 500\n"
    "🥉 3 місце — $500\n\n"
    "Поїхали?"
)

NAME_PROMPT = "Напиши своє ім'я та прізвище:"
NAME_ERROR = "Напиши ім'я та прізвище разом через пробіл."

EMAIL_PROMPT = "Твій email:"
EMAIL_ERROR = "В email помилка. Перевір і надішли ще раз."

TELEGRAM_PROMPT = "Твій Telegram-нік для зв'язку:"
TELEGRAM_CONFIRM = "Твій нік в телеграм — {username}.\nПідтверджуєш?"
TELEGRAM_ERROR = "Нік має починатися з @ і містити щонайменше 5 символів."

SOCIAL_PROMPT = "Посилання на твій LinkedIn або іншу соцмережу:"
SOCIAL_ERROR = "Скинь URL або тицяй 'Пропустити'."

WORKS_PROMPT = "Посилання на твої роботи (GitHub, сайт, демо):"
WORKS_ERROR = "Скинь хоча б одне посилання на роботу/GitHub або тицяй 'Пропустити'."

ROLE_PROMPT = "Твоя спеціалізація:"
ROLE_OTHER_PROMPT = "Опиши свою спеціалізацію:"

WORKPLACE_PROMPT = "Де зараз працюєш?"
WORKPLACE_OTHER_PROMPT = "Опиши, де працюєш:"

LLM_PROMPT = "Твій досвід з LLM та ШІ-агентами?"

TOOLS_PROMPT = "Інструменти, які плануєш юзати (можна кілька):"

PROJECT_PROMPT = (
    "Розкажи про свій найкрутіший AI-проєкт "
    "(стек, завдання, що було найважче - 2-4 речення):"
)
PROJECT_ERROR = "Напиши трохи детальніше (мінімум 50 символів)."

SOURCE_PROMPT = "Звідки дізнався про хакатон?"
SOURCE_OTHER_PROMPT = "Звідки саме дізнався?"

CONSENT_TEXT = (
    "Потрібна згода на обробку персональних даних "
    f"(<a href='{{privacy_url}}'>Політика приватності</a>):"
)
CONSENT_DENIED = (
    "Без згоди на обробку даних ми не можемо завершити реєстрацію.\n"
    "Якщо передумаєш — натисни /start."
)

UNKNOWN_INPUT = (
    "Я тебе не зрозумів. Будь ласка, скористайся меню (/menu) "
    "або дай відповідь на поточне питання реєстрації."
)

RESUME_PROMPT = (
    "Ти вже починав реєстрацію. Що робимо?"
)

REGISTRATION_COMPLETE = (
    "✅ Реєстрацію завершено! Дані збережено.\n"
    "Ось головне меню — /menu"
)

FEEDBACK_PROMPT = (
    "Напиши своє повідомлення — ми перешлемо його адміну.\n"
    "Адмін відповість у цей чат.\n"
    "Для виходу: /menu або /start"
)

FEEDBACK_SENT = "Повідомлення надіслано адміну! Очікуй відповіді."

ROLE_LABELS = {
    "developer": "💻 Developer",
    "product_design": "🎨 Product / Design",
    "marketing_growth": "📈 Marketing / Growth",
    "student": "🎓 Student",
    "other": "✏️ Інше",
}

WORKPLACE_LABELS = {
    "ecommerce": "🛒 E-commerce",
    "saas": "☁️ SaaS",
    "agency_freelance": "🏢 Agency / Freelance",
    "enterprise": "🏛 Enterprise",
    "student_intern": "🎓 Student / Intern",
    "other": "✏️ Інше",
}

LLM_LABELS = {
    "production": "🚀 В проді",
    "experiments": "🧪 Пет-проєкти",
    "beginner": "🌱 Починаю",
}

SOURCE_LABELS = {
    "linkedin": "LinkedIn",
    "telegram": "Telegram",
    "discord": "Discord",
    "dou": "DOU",
    "friends": "Від друзів",
    "other": "Інше",
}

TOOL_OPTIONS = [
    "Claude API",
    "OpenAI API",
    "LangChain/LangGraph",
    "LlamaIndex",
    "n8n/Make",
    "Python",
    "Other",
]

FIELD_LABELS = {
    "full_name": "👤 Ім'я",
    "email": "📧 Email",
    "telegram_username": "💬 Telegram",
    "social_media": "🔗 Соцмережа",
    "portfolio_links": "💼 Роботи",
    "occupation": "🎯 Спеціалізація",
    "workplace": "🏢 Робота",
    "llm_experience": "🤖 LLM досвід",
    "tools": "🛠 Інструменти",
    "coolest_project": "⭐ Проєкт",
    "traffic_source": "📣 Джерело",
}
