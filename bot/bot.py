import os
import json
import random
import asyncio
from datetime import datetime
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart, Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
USER_ID = int(os.getenv("USER_ID"))

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# --- Кнопки ---
main_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📅 Расписание", callback_data="schedule")],
    [InlineKeyboardButton(text="🧠 Цели", callback_data="goals"), InlineKeyboardButton(text="✅ Чеклист", callback_data="checklist")],
    [InlineKeyboardButton(text="📈 Прогресс", callback_data="progress")]
])

goal_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="➕ Добавить цель", callback_data="add_goal")]
])

checklist_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="➕ Добавить задачу", callback_data="add_task")]
])

# --- Вспомогательные функции ---
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

def get_progress_bar(current, total):
    filled = int(10 * current / total)
    return "▓" * filled + "░" * (10 - filled)

# --- Хэндлеры ---
@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Привет, Ден! Я твой помощник по распорядку дня!", reply_markup=main_kb)

@dp.callback_query(F.data == "schedule")
async def show_schedule(callback: types.CallbackQuery):
    schedule = load_json("data/schedule.json", [])
    text = "📅 Расписание на день:\n" + "\n".join([f"{item['time']} — {item['activity']}" for item in schedule])
    await callback.message.answer(text)
    await callback.answer()

@dp.callback_query(F.data == "goals")
async def show_goals(callback: types.CallbackQuery):
    goals = load_json("data/goals.json", [])
    total = len(goals)
    done = sum([1 for g in goals if g.get("done")])
    progress = get_progress_bar(done, total) if total else "—"

    if goals:
        text = "🧠 Твои цели:\n" + "\n".join([f"{i+1}. {'✅' if g.get('done') else '⬜'} {g['text']}" for i, g in enumerate(goals)])
        text += f"\n\nПрогресс: {progress}"
    else:
        text = "Пока целей нет."

    await callback.message.answer(text, reply_markup=goal_kb)
    await callback.answer()

@dp.callback_query(F.data == "add_goal")
async def prompt_add_goal(callback: types.CallbackQuery):
    await callback.message.answer("✍️ Напиши свою цель одним сообщением:")
    dp['add_goal'] = True
    await callback.answer()

@dp.message()
async def handle_goal_text(message: Message):
    if dp.get('add_goal'):
        dp['add_goal'] = False
        goals = load_json("data/goals.json", [])
        goals.append({"text": message.text, "done": False})
        save_json("data/goals.json", goals)
        await message.answer("🎯 Цель добавлена!", reply_markup=main_kb)

@dp.callback_query(F.data == "checklist")
async def show_checklist(callback: types.CallbackQuery):
    checklist = load_json("data/checklist.json", [])
    today = datetime.today().strftime("%Y-%m-%d")
    today_tasks = [t for t in checklist if t.get("date") == today]
    total = len(today_tasks)
    done = sum([1 for t in today_tasks if t.get("done")])
    progress = get_progress_bar(done, total) if total else "—"

    if today_tasks:
        text = "✅ Чеклист на сегодня:\n" + "\n".join([f"{i+1}. {'✅' if t.get('done') else '⬜'} {t['task']}" for i, t in enumerate(today_tasks)])
        text += f"\n\nПрогресс: {progress}"
    else:
        text = "Сегодняшний чеклист пуст."

    await callback.message.answer(text, reply_markup=checklist_kb)
    await callback.answer()

@dp.callback_query(F.data == "add_task")
async def prompt_add_task(callback: types.CallbackQuery):
    await callback.message.answer("✍️ Напиши задачу одним сообщением:")
    dp['add_task'] = True
    await callback.answer()

@dp.message()
async def handle_task_text(message: Message):
    if dp.get('add_task'):
        dp['add_task'] = False
        checklist = load_json("data/checklist.json", [])
        checklist.append({"task": message.text, "done": False, "date": datetime.today().strftime("%Y-%m-%d")})
        save_json("data/checklist.json", checklist)
        await message.answer("📝 Задача добавлена!", reply_markup=main_kb)

# --- Запуск ---
async def main():
    scheduler = AsyncIOScheduler()
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        print("[INFO] Бот запускается...")
        asyncio.run(main())
    except Exception as e:
        print("[ERROR] Ошибка при запуске:", e)
