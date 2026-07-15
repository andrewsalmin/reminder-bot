from aiogram import Dispatcher

from . import delete_reminders_handlers, common_handlers, main_handlers, set_timezone_handlers

def register_handlers(dp: Dispatcher) -> None:
    dp.include_router(common_handlers.router)
    dp.include_router(set_timezone_handlers.router)
    dp.include_router(delete_reminders_handlers.router)
    dp.include_router(main_handlers.router)