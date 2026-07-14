from aiogram.filters import BaseFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.states import MenuStates
from database import get_registration

TEXT_INPUT_STATES = frozenset(
    {
        "name",
        "email",
        "telegram_username",
        "social",
        "works",
        "role_other",
        "workplace_other",
        "project",
        "source_other",
    }
)


class RegistrationTextFilter(BaseFilter):
    async def __call__(
        self,
        message: Message,
        state: FSMContext,
    ) -> bool | dict[str, str]:
        if await state.get_state() == MenuStates.feedback.state:
            return False

        reg = get_registration(message.from_user.id)
        if not reg or reg.get("is_completed"):
            return False
        current = reg.get("current_state")
        if current not in TEXT_INPUT_STATES:
            return False
        return {"reg_state": current}
