import re

EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
URL_RE = re.compile(
    r"^https?://[^\s/$.?#].[^\s]*$",
    re.IGNORECASE,
)
TELEGRAM_USERNAME_RE = re.compile(r"^@[a-zA-Z0-9_]{4,31}$")


def validate_full_name(text: str) -> bool:
    text = text.strip()
    return len(text) >= 3 and " " in text


def validate_email(text: str) -> bool:
    return bool(EMAIL_RE.match(text.strip()))


def validate_telegram_username(text: str) -> bool:
    username = text.strip()
    if not username.startswith("@"):
        username = f"@{username}"
    return bool(TELEGRAM_USERNAME_RE.match(username)) and len(username) >= 5


def normalize_telegram_username(text: str) -> str:
    username = text.strip()
    if not username.startswith("@"):
        username = f"@{username}"
    return username


def validate_url(text: str) -> bool:
    return bool(URL_RE.match(text.strip()))


def extract_urls(text: str) -> list[str]:
    return [part for part in re.findall(r"https?://\S+", text) if validate_url(part)]


def validate_portfolio(text: str) -> bool:
    return len(extract_urls(text)) >= 1


def validate_project(text: str) -> bool:
    return len(text.strip()) >= 50
