import os
import json
import random
import asyncio
from datetime import datetime
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from keyboards import main_menu_kb, checklist_inline_kb, goals_inline_kb

# Загрузка переменных окружения
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
USER_ID = int(os.getenv("USER_ID", 0))

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

# Состояния для FSM
class Form(StatesGroup):
    waiting_for_task = State()
    waiting_for_goal = State()

# --- Утилиты ---
def load_json(path, default=[]):
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return default

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_random_quote():
    try:
        with open("data/quotes.txt", encoding="utf-8") as f:
            quotes = [line.strip() for line in f if line.strip()]
        return random.choice(quotes)
    except Exception:
        return "Каждый день — шанс начать заново."

# --- Команды ---
@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Привет! Я твой ИИ-помощник!", reply_markup=main_menu_kb)

@dp.message(Command("помощь"))
async def help_cmd(message: Message):
    await message.answer("Выбери действие из меню ⬇️")

@dp.message(F.text == "📅 Расписание")
async def schedule(message: Message):
    await message.answer("Здесь будет твое расписание ✨")

@dp.message(F.text == "✅ Чеклист")
async def checklist(message: Message):
    tasks = load_json("data/checklist.json")
    if not tasks:
        return await message.answer("Чеклист пуст. ✍️ Добавь задачи.", reply_markup=checklist_inline_kb)

    text = "📋 Чеклист:\n"
    completed = 0
    for i, task in enumerate(tasks):
        status = "✅" if task.get("done") else "⬜️"
        if task.get("done"): completed += 1
        text += f"{status} {task['task']}\n"
    percent = min(10, max(0, int((completed / len(tasks)) * 10)))
    bar = "▮" * percent + "▯" * (10 - percent)
    text += f"\nПрогресс: {bar}"
    await message.answer(text, reply_markup=checklist_inline_kb)

@dp.message(F.text == "🎯 Цели")
async def goals(message: Message):
    goals = load_json("data/goals.json")
    if not goals:
        return await message.answer("Целей пока нет 🎯", reply_markup=goals_inline_kb)

    text = "🎯 Цели:\n"
    completed = 0
    for i, goal in enumerate(goals):
        status = "✅" if goal.get("done") else "⬜️"
        if goal.get("done"): completed += 1
        text += f"{status} {goal['goal']}\n"
    percent = min(10, max(0, int((completed / len(goals)) * 10)))
    bar = "▮" * percent + "▯" * (10 - percent)
    text += f"\nПрогресс: {bar}"
    await message.answer(text, reply_markup=goals_inline_kb)

@dp.message(F.text == "📈 Прогресс")
async def progress(message: Message):
    await goals(message)
    await checklist(message)

# --- Inline кнопки ---
@dp.callback_query(F.data == "add_task")
async def add_task_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Напиши новую задачу:")
    await state.set_state(Form.waiting_for_task)
    await callback.answer()

@dp.callback_query(F.data == "add_goal")
async def add_goal_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Напиши новую цель:")
    await state.set_state(Form.waiting_for_goal)
    await callback.answer()

@dp.message(Form.waiting_for_task)
async def process_new_task(message: Message, state: FSMContext):
    tasks = load_json("data/checklist.json")
    tasks.append({"task": message.text, "done": False})
    save_json("data/checklist.json", tasks)
    await message.answer("Задача добавлена ✅")
    await state.clear()

@dp.message(Form.waiting_for_goal)
async def process_new_goal(message: Message, state: FSMContext):
    goals = load_json("data/goals.json")
    goals.append({"goal": message.text, "done": False})
    save_json("data/goals.json", goals)
    await message.answer("Цель добавлена 🎯")
    await state.clear()

@dp.callback_query(F.data == "task_done")
async def mark_task_done(callback: CallbackQuery):
    tasks = load_json("data/checklist.json")
    for task in tasks:
        if not task.get("done"):
            task["done"] = True
            break
    save_json("data/checklist.json", tasks)
    await callback.message.answer("Отметил задачу как выполненную ✅")
    await callback.answer()

@dp.callback_query(F.data == "goal_done")
async def mark_goal_done(callback: CallbackQuery):
    goals = load_json("data/goals.json")
    for goal in goals:
        if not goal.get("done"):
            goal["done"] = True
            break
    save_json("data/goals.json", goals)
    await callback.message.answer("Цель достигнута 🎯✅")
    await callback.answer()

@dp.callback_query(F.data == "task_failed")
async def task_failed(callback: CallbackQuery):
    await callback.message.answer("Задача отложена ⏳")
    await callback.answer()

@dp.callback_query(F.data == "goal_failed")
async def goal_failed(callback: CallbackQuery):
    await callback.message.answer("Цель пока не достигнута 🕐")
    await callback.answer()

# --- Главный запуск ---
async def main():
    scheduler = AsyncIOScheduler()
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
