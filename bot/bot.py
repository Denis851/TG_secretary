import asyncio
import json
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from keyboards import main_menu_kb, checklist_inline_kb, goals_inline_kb

# Инициализация бота
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
scheduler = AsyncIOScheduler()

# ===== Хелперы =====
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

def progress_bar(completed, total):
    percent = int((completed / total) * 10) if total else 0
    return "📊 " + "🟩" * percent + "⬜️" * (10 - percent) + f" {completed}/{total}"

# ===== Хендлеры =====
@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Привет, Ден! Я твой помощник по распорядку дня!", reply_markup=main_menu_kb)

@dp.message(lambda m: m.text == "📅 Расписание")
async def show_schedule(message: Message):
    schedule = load_json("data/schedule.json")
    if not schedule:
        await message.answer("Расписание пока не добавлено.")
        return
    text = "<b>📅 Текущее расписание:</b>\n" + "\n".join(schedule)
    await message.answer(text)

@dp.message(F.text.lower() == "✅ чеклист")
async def show_checklist(message: Message):
    tasks = load_json("data/checklist.json", [])
    if not tasks:
        await message.answer("Задачи пока не добавлены.", reply_markup=checklist_inline_kb)
        return
    text = "📋 Текущий чеклист:\n" + "\n".join(f"{i+1}. {t}" for i, t in enumerate(tasks))
    await message.answer(text, reply_markup=checklist_inline_kb)


@dp.message(F.text.lower() == "🎯 цели")
async def show_goals(message: Message):
    goals = load_json("data/goals.json", [])
    if not goals:
        await message.answer("Цели пока не добавлены.", reply_markup=goals_inline_kb)
        return
    text = "🎯 Текущие цели:\n" + "\n".join(f"{i+1}. {g}" for i, g in enumerate(goals))
    await message.answer(text, reply_markup=goals_inline_kb)


@dp.message(lambda m: m.text == "📈 Прогресс")
async def show_progress(message: Message):
    tasks = load_json("data/checklist.json")
    goals = load_json("data/goals.json")
    total = len(tasks) + len(goals)
    done = len([t for t in tasks if t.startswith("✅")]) + len([g for g in goals if g.startswith("✅")])
    bar = progress_bar(done, total)
    await message.answer(f"<b>Общий прогресс:</b>\n{bar}")

# ===== Callback =====
@dp.callback_query(lambda c: c.data == "add_task")
async def add_task_prompt(callback: CallbackQuery):
    await callback.message.answer("Напиши задачу, которую хочешь добавить:")
    await callback.answer()

@dp.message(lambda m: m.reply_to_message and "добавить задачу" in m.reply_to_message.text.lower())
async def save_task(message: Message):
    tasks = load_json("data/checklist.json")
    tasks.append(message.text)
    save_json("data/checklist.json", tasks)
    await message.answer("Задача добавлена!")

@dp.callback_query(lambda c: c.data == "add_goal")
async def add_goal_prompt(callback: CallbackQuery):
    await callback.message.answer("Напиши цель, которую хочешь добавить:")
    await callback.answer()

@dp.message(lambda m: m.reply_to_message and "добавить цель" in m.reply_to_message.text.lower())
async def save_goal(message: Message):
    goals = load_json("data/goals.json")
    goals.append(message.text)
    save_json("data/goals.json", goals)
    await message.answer("Цель добавлена!")

# ===== MAIN =====
async def main():
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
