import os
import json
import random
import asyncio
from datetime import datetime
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, CallbackQuery, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart, Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Загрузка переменных окружения
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
USER_ID = int(os.getenv("USER_ID"))

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Главная клавиатура (Inline)
main_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📅 Расписание", callback_data="menu_schedule")],
    [InlineKeyboardButton(text="🧠 Цели", callback_data="menu_goals")],
    [InlineKeyboardButton(text="✅ Чеклист", callback_data="menu_checklist")],
    [InlineKeyboardButton(text="📈 Прогресс", callback_data="menu_progress")]
])

# Вспомогательные функции

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

async def send_quote(bot: Bot, user_id: int):
    quote = get_random_quote()
    await bot.send_message(user_id, f"💬 Цитата дня:\n{quote}")

# Команды

@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Привет, Ден! Я твой помощник по распорядку дня!", reply_markup=main_kb)

@dp.callback_query(F.data == "menu_schedule")
async def menu_schedule(callback: CallbackQuery):
    schedule = load_json("data/schedule.json", [])
    text = "📅 Расписание на день:\n" + "\n".join([f"{item['time']} — {item['activity']}" for item in schedule])
    await callback.message.answer(text)
    await callback.answer()

@dp.callback_query(F.data == "menu_checklist")
async def menu_checklist(callback: CallbackQuery):
    checklist = load_json("data/checklist.json", [])
    if not checklist:
        await callback.message.answer("Чеклист пуст. Добавь задачи.")
    else:
        text = "📝 Чеклист задач:\n" + "\n".join([f"- {item['task']}" for item in checklist])
        await callback.message.answer(text)
    await callback.answer()

@dp.callback_query(F.data == "menu_goals")
async def menu_goals(callback: CallbackQuery):
    goals = load_json("data/goals.json", [])
    if not goals:
        await callback.message.answer("Целей пока нет.")
    else:
        text = "🎯 Твои цели:\n" + "\n".join([f"- {g}" for g in goals])
        await callback.message.answer(text)
    await callback.answer()

@dp.callback_query(F.data == "menu_progress")
async def menu_progress(callback: CallbackQuery):
    checklist = load_json("data/checklist.json", [])
    goals = load_json("data/goals.json", [])
    done_tasks = [t for t in checklist if t.get("done")]
    done_goals = [g for g in goals if isinstance(g, dict) and g.get("done")]

    progress = (len(done_tasks) + len(done_goals)) / max(len(checklist) + len(goals), 1) * 100
    await callback.message.answer(f"📈 Прогресс выполнения: {int(progress)}%")
    await callback.answer()

# Планировщик
async def main():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_quote, 'cron', hour=6, minute=0, args=[bot, USER_ID])
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        print("[INFO] Бот запускается...")
        asyncio.run(main())
    except Exception as e:
        print("[ERROR] Ошибка при запуске:", e)
