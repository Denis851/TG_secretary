import asyncio
import json
import os
from aiogram import Bot, Dispatcher, F, types
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from keyboards import main_menu_kb, checklist_inline_kb, goals_inline_kb

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()
scheduler = AsyncIOScheduler()

# ======================== Работа с файлами =========================

def load_json(path, default=[]):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ======================== Хендлеры =========================

@dp.message(F.text.lower() == "/start")
async def cmd_start(message: Message):
    await message.answer("Привет, Ден! Я твой помощник по распорядку дня!", reply_markup=main_menu_kb)

@dp.message(F.text.lower() == "📅 расписание")
async def show_schedule(message: Message):
    schedule = load_json("data/schedule.json")
    if not schedule:
        await message.answer("📅 Расписание пока не задано.")
    else:
        text = "\n".join([f"{item['time']} — {item['activity']}" for item in schedule])
        await message.answer(f"📅 Текущее расписание:\n{text}")

@dp.message(F.text.lower() == "✅ чеклист")
async def show_checklist(message: Message):
    tasks = load_json("data/checklist.json")
    if not tasks:
        await message.answer("✅ Чеклист пуст. Добавь задачу!", reply_markup=checklist_inline_kb)
    else:
        text = "\n".join(tasks)
        await message.answer(f"📋 Текущий чеклист:\n{text}", reply_markup=checklist_inline_kb)

@dp.message(F.text.lower() == "🎯 цели")
async def show_goals(message: Message):
    goals = load_json("data/goals.json")
    if not goals:
        await message.answer("🎯 Целей пока нет. Добавь новую!", reply_markup=goals_inline_kb)
    else:
        text = "\n".join(goals)
        await message.answer(f"🎯 Текущие цели:\n{text}", reply_markup=goals_inline_kb)

@dp.message(F.text.lower() == "📈 прогресс")
async def show_progress(message: Message):
    tasks = load_json("data/checklist.json")
    goals = load_json("data/goals.json")
    completed = len([t for t in tasks if t.startswith("✅")]) + len([g for g in goals if g.startswith("✅")])
    total = len(tasks) + len(goals)
    percent = int((completed / total) * 100) if total else 0
    bar = "🟩" * (percent // 10) + "⬜️" * (10 - percent // 10)
    await message.answer(f"📊 Прогресс: {bar} {percent}%")

# ======================== Inline действия =========================

@dp.callback_query(F.data == "add_task")
async def ask_new_task(callback: types.CallbackQuery):
    await callback.message.answer("✍️ Введи новую задачу:")
    await callback.answer()
    dp.message.register(save_task, F.text)

async def save_task(message: Message):
    tasks = load_json("data/checklist.json")
    tasks.append(message.text)
    save_json("data/checklist.json", tasks)
    await message.answer("✅ Задача добавлена!")
    dp.message.unregister(save_task)

@dp.callback_query(F.data == "add_goal")
async def ask_new_goal(callback: types.CallbackQuery):
    await callback.message.answer("🎯 Введи новую цель:")
    await callback.answer()
    dp.message.register(save_goal, F.text)

async def save_goal(message: Message):
    goals = load_json("data/goals.json")
    goals.append(message.text)
    save_json("data/goals.json", goals)
    await message.answer("🎯 Цель добавлена!")
    dp.message.unregister(save_goal)

@dp.callback_query(F.data == "task_done")
async def mark_task_done(callback: types.CallbackQuery):
    tasks = load_json("data/checklist.json")
    if tasks:
        tasks[0] = f"✅ {tasks[0]}"
        save_json("data/checklist.json", tasks)
        await callback.message.answer("Задача выполнена!")
    await callback.answer()

@dp.callback_query(F.data == "goal_done")
async def mark_goal_done(callback: types.CallbackQuery):
    goals = load_json("data/goals.json")
    if goals:
        goals[0] = f"✅ {goals[0]}"
        save_json("data/goals.json", goals)
        await callback.message.answer("Цель выполнена!")
    await callback.answer()

# ======================== Запуск =========================

async def main():
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
