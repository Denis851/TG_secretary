import os
import json
import random
import asyncio
from datetime import datetime
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, FSInputFile, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
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

# --- Клавиатура ---
main_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="🌅 Утро"), KeyboardButton(text="💻 Продуктивность")],
    [KeyboardButton(text="🧘 Отдых"), KeyboardButton(text="📊 Отчёт")],
    [KeyboardButton(text="📆 Распорядок дня")]
], resize_keyboard=True)

mood_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="😊", callback_data="mood_happy"),
     InlineKeyboardButton(text="😐", callback_data="mood_neutral"),
     InlineKeyboardButton(text="😞", callback_data="mood_sad")]
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

# --- Распорядок дня ---
@dp.message(F.text.lower() == "📆 распорядок дня")
async def show_schedule(message: Message):
    schedule = load_json("data/daily_schedule.json", [])
    if not schedule:
        await message.answer("Расписание дня пока не задано. Добавьте его в файл data/daily_schedule.json")
        return
    text = "📅 <b>Твой распорядок дня:</b>\n"
    for item in schedule:
        text += f"⏰ <b>{item['time']}</b>: {item['activity']}\n"
    await message.answer(text, parse_mode="HTML")

# --- Главная функция запуска ---
async def main():
    scheduler = AsyncIOScheduler()
    # Ежедневная цитата
    scheduler.add_job(send_quote, 'cron', hour=6, minute=0, args=[bot, USER_ID])
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        print("[INFO] Бот запускается...")
        asyncio.run(main())
    except Exception as e:
        print("[ERROR] Ошибка при запуске:", e)
