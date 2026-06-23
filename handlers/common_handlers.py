import logging

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from utils.misc import commands

router = Router()
logger = logging.getLogger(__name__)

@router.message(lambda m: m.text in ['/cancel', commands.get('cancel')])
async def cancel_action(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()

    if current_state is None:
        await message.answer(
            'Нет активных действий для отмены ⚠️',
            reply_markup=ReplyKeyboardRemove(),
        )
        return

    await state.clear()
    await message.answer(
        'Действие отменено ❌',
        reply_markup=ReplyKeyboardRemove(),
    )