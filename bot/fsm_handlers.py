from aiogram import Router
from aiogram.types import Message
from bot.fsm_states import GoalStates, TaskStates

router = Router()

# Обработчики для состояний
async def goal_handler(message: Message):
    await message.answer("Цель принята!")

async def task_handler(message: Message):
    await message.answer("Задача принята!")

def register_fsm_handlers(r: Router):
    r.message.register(goal_handler, GoalStates.waiting_for_goal_text)
    r.message.register(task_handler, TaskStates.waiting_for_task_text)
