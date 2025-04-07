# bot.py — Денис Фокус v2 (финальная версия)

import os
import json
import random
import asyncio
from datetime import datetime
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F, types
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart, Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
USER_ID = int(os.getenv("USER_ID"))

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Клавиатура главного меню
main_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="📅 Расписание"), KeyboardButton(text="🧠 Цели")],
    [KeyboardButton(text="✅ Чеклист"), KeyboardButton(text="✈️ Прогресс")]
], resize_keyboard=True)

# Вспомогательные функции
def load_json(path, default=[]):
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except:
        return default

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_progress_bar(completed, total):
    percent = int((completed / total) * 10) if total > 0 else 0
    return "█" * percent + "░" * (10 - percent) + f" {completed}/{total}"

# Обработчики
@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Привет, Ден! Я твой помощник по распорядку дня!", reply_markup=main_kb)

@dp.message(F.text.lower() == "📅 расписание")
async def show_schedule(message: Message):
    schedule = load_json("data/schedule.json")
    text = "<b>📅 Расписание:</b>\n"
    for item in schedule:
        text += f"<b>{item['time']}</b> — {item['activity']}\n"
    await message.answer(text)

@dp.message(F.text.lower() == "🧠 цели")
async def show_goals(message: Message):
    goals = load_json("data/goals.json")
    if not goals:
        await message.answer("Целей пока нет. Добавь их с помощью кнопки!")
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"✅ {g['text']}" if g['done'] else f"⬜️ {g['text']}", callback_data=f"goal_{i}")]
        for i, g in enumerate(goals)
    ])
    await message.answer("<b>🧠 Цели:</b>", reply_markup=kb)

@dp.message(F.text.lower() == "✅ чеклист")
async def show_checklist(message: Message):
    checklist = load_json("data/checklist.json")
    if not checklist:
        await message.answer("Чеклист пуст. Добавь задачи с помощью кнопки!")
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"✅ {item['task']}" if item['done'] else f"⬜️ {item['task']}", callback_data=f"task_{i}")]
        for i, item in enumerate(checklist)
    ])
    await message.answer("<b>✅ Чеклист:</b>", reply_markup=kb)

@dp.message(F.text.lower() == "✈️ прогресс")
async def show_progress(message: Message):
    goals = load_json("data/goals.json")
    checklist = load_json("data/checklist.json")
    g_done = len([g for g in goals if g['done']])
    t_done = len([t for t in checklist if t['done']])
    text = (
        f"<b>✈️ Прогресс:</b>\n"
        f"Цели: {get_progress_bar(g_done, len(goals))}\n"
        f"Задачи: {get_progress_bar(t_done, len(checklist))}"
    )
    await message.answer(text)

# Обработка выполнения целей/задач
@dp.callback_query(F.data.startswith("goal_"))
async def complete_goal(callback: types.CallbackQuery):
    index = int(callback.data.split("_")[1])
    goals = load_json("data/goals.json")
    goals[index]["done"] = not goals[index].get("done", False)
    save_json("data/goals.json", goals)
    await callback.answer("Готово!")
    await show_goals(callback.message)

@dp.callback_query(F.data.startswith("task_"))
async def complete_task(callback: types.CallbackQuery):
    index = int(callback.data.split("_")[1])
    checklist = load_json("data/checklist.json")
    checklist[index]["done"] = not checklist[index].get("done", False)
    save_json("data/checklist.json", checklist)
    await callback.answer("Отмечено!")
    await show_checklist(callback.message)

# Планировщик цитат (пример напоминания)
def get_random_quote():
    try:
        with open("data/quotes.txt", encoding="utf-8") as f:
            quotes = [line.strip() for line in f if line.strip()]
        return random.choice(quotes)
    except:
        return "Каждый день — шанс начать заново."

async def send_quote():
    quote = get_random_quote()
    await bot.send_message(USER_ID, f"💬 Цитата дня:\n{quote}")

async def main():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_quote, 'cron', hour=6, minute=0)  # пример автонапоминания
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        print("[INFO] Бот запускается...")
        asyncio.run(main())
    except Exception as e:
        print("[ERROR] Ошибка:", e)
