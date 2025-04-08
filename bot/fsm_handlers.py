from aiogram import Router
from aiogram.types import Message
from .fsm_states import GoalStates, TaskStates

router = Router()

# Обработчики для состояний
@router.message(GoalStates.waiting_for_goal_text)
async def goal_handler(message: Message):
    await message.answer("Цель принята!")

@router.message(TaskStates.waiting_for_task_text)
async def task_handler(message: Message):
    await message.answer("Задача принята!")

# Регистрируем хендлеры
def register_fsm_handlers(router: Router):
    router.message.register(goal_handler, GoalStates.waiting_for_goal_text)
    router.message.register(task_handler, TaskStates.waiting_for_task_text)

