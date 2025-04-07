from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.markdown import hbold
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters.command import CommandStart
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.client.default import DefaultBotProperties
import asyncio
import os
import json
from keyboards import main_menu_kb, checklist_inline_kb, goals_inline_kb

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
scheduler = AsyncIOScheduler()

waiting_for_task = set()
waiting_for_goal = set()

# JSON helpers
def load_json(path, default=[]):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Прогресс бар
def progress_bar(completed, total):
    if total == 0:
        return "▫️" * 20 + " 0/0"
    percent = int((completed / total) * 20)
    return "🟩" * percent + "▫️" * (20 - percent) + f" {completed}/{total}"

# Старт
@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Привет, Ден! Я твой помощник по распорядку дня!", reply_markup=main_menu_kb)

# Расписание
@dp.message(F.text.lower() == "📅 расписание")
async def show_schedule(message: Message):
    schedule = load_json("data/schedule.json")
    if not schedule:
        await message.answer("Расписание пока не добавлено.")
    else:
        await message.answer("\n".join(schedule))

# Чеклист
@dp.message(F.text.lower() == "✅ чеклист")
async def show_checklist(message: Message):
    tasks = load_json("data/checklist.json")
    if not tasks:
        await message.answer("Задачи пока не добавлены.", reply_markup=checklist_inline_kb)
    else:
        text = "\n".join([f"{i+1}. {t}" for i, t in enumerate(tasks)])
        await message.answer(f"Текущий чеклист:\n{text}", reply_markup=checklist_inline_kb)

# Цели
@dp.message(F.text.lower() == "🎯 цели")
async def show_goals(message: Message):
    goals = load_json("data/goals.json")
    if not goals:
        await message.answer("Цели пока не добавлены.", reply_markup=goals_inline_kb)
    else:
        text = "\n".join([f"{i+1}. {g}" for i, g in enumerate(goals)])
        await message.answer(f"Текущие цели:\n{text}", reply_markup=goals_inline_kb)

# Прогресс
@dp.message(F.text.lower() == "📈 прогресс")
async def show_progress(message: Message):
    tasks = load_json("data/checklist.json")
    goals = load_json("data/goals.json")
    total = len(tasks) + len(goals)
    completed = len([t for t in tasks if t.startswith("✅")]) + len([g for g in goals if g.startswith("✅")])
    bar = progress_bar(completed, total)
    await message.answer(f"📊 Общий прогресс:\n{bar}")

# Обработка inline-кнопок
@dp.callback_query(F.data == "add_task")
async def handle_add_task(callback: types.CallbackQuery):
    await callback.message.answer("Введи текст задачи:")
    waiting_for_task.add(callback.from_user.id)
    await callback.answer()

@dp.callback_query(F.data == "add_goal")
async def handle_add_goal(callback: types.CallbackQuery):
    await callback.message.answer("Введи текст цели:")
    waiting_for_goal.add(callback.from_user.id)
    await callback.answer()

@dp.message(F.text)
async def handle_text_entry(message: Message):
    if message.from_user.id in waiting_for_task:
        tasks = load_json("data/checklist.json")
        tasks.append(message.text)
        save_json("data/checklist.json", tasks)
        waiting_for_task.remove(message.from_user.id)
        await message.answer("Задача добавлена ✅")
    elif message.from_user.id in waiting_for_goal:
        goals = load_json("data/goals.json")
        goals.append(message.text)
        save_json("data/goals.json", goals)
        waiting_for_goal.remove(message.from_user.id)
        await message.answer("Цель добавлена ✅")

# Запуск
async def main():
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
