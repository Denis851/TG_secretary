from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from fsm_states import TaskStates, GoalStates
from keyboards import checklist_inline_kb, goals_inline_kb
from utils import load_json, save_json

router = Router()

# === ДОБАВЛЕНИЕ ЦЕЛИ ===
@router.callback_query(F.data == "add_goal")
async def add_goal_start(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Напиши новую цель:")
    await state.set_state(GoalStates.waiting_for_goal_text)
    await call.answer()

@router.message(GoalStates.waiting_for_goal_text)
async def process_goal_text(message: Message, state: FSMContext):
    goals = load_json("data/goals.json")
    goals.append(message.text)
    save_json("data/goals.json", goals)
    await message.answer("🎯 Цель добавлена!", reply_markup=goals_inline_kb)
    await state.clear()

# === ДОБАВЛЕНИЕ ЗАДАЧИ ===
@router.callback_query(F.data == "add_task")
async def add_task_start(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Напиши новую задачу:")
    await state.set_state(TaskStates.waiting_for_task_text)
    await call.answer()

@router.message(TaskStates.waiting_for_task_text)
async def process_task_text(message: Message, state: FSMContext):
    tasks = load_json("data/checklist.json")
    tasks.append(message.text)
    save_json("data/checklist.json", tasks)
    await message.answer("✅ Задача добавлена!", reply_markup=checklist_inline_kb)
    await state.clear()
