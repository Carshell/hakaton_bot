from aiogram import Router

from bot.handlers.admin import router as admin_router
from bot.handlers.feedback import router as feedback_router
from bot.handlers.menu import router as menu_router
from bot.handlers.registration import router as registration_router


def get_routers() -> list[Router]:
    return [
        admin_router,
        feedback_router,
        registration_router,
        menu_router,
    ]
