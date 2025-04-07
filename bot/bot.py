import os
import json
import random
import asyncio
from datetime import datetime
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types, F
from aiogram.types import (
    Message, FSInputFile, ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart, Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Загрузка переменных окружения
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
USER_ID = int(os.getenv("USER_ID"))

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# ---------- Клавиатуры ----------
main_kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [KeyboardButton(text="📅 Расписание"), KeyboardButton(text="📝 Чеклист")],
    [KeyboardButton(text="🎯 Цели"), KeyboardButton(text="💬 Цитата")]
])

mood_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="😊", callback_data="mood_happy"),
        InlineKeyboardButton(text="😐", callback_data="mood_neutral"),
        InlineKeyboardButton(text="😞", callback_data="mood_sad"),
    ]
])

# ---------- Функции ----------
def load_json(path, default=[]):
    try:
        with open(path, encoding="utf-8") as f:
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
    await bot.send_message(user_id, f"💬 Цитата дня:\n<i>{quote}</i>", parse_mode="HTML")

# ---------- Расписание по умолчанию ----------
def get_default_schedule():
    return [
        {"time": "05:30", "activity": "Подъём, вода, разминка, медитация"},
        {"time": "06:00", "activity": "Утренняя тренировка"},
        {"time": "07:00", "activity": "Работа / Фриланс"},
        {"time": "09:30", "activity": "Перерыв (чай, прогулка)"},
        {"time": "10:00", "activity": "Обучение / Саморазвитие"},
        {"time": "11:30", "activity": "Обед + близкие"},
        {"time": "12:30", "activity": "Работа 2"},
        {"time": "14:30", "activity": "Отдых / Сон"},
        {"time": "15:30", "activity": "Креатив / Проекты"},
        {"time": "17:00", "activity": "Семья / Прогулка"},
        {"time": "19:00", "activity": "Ужин, отдых"},
        {"time": "20:00", "activity": "Личное время"},
        {"time": "21:30", "activity": "Подготовка ко сну"},
        {"time": "22:00", "activity": "Сон"},
    ]

# ---------- Обработчики ----------
@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("👋 Привет, Денис! Готов идти по расписанию?", reply_markup=main_kb)

@dp.message(F.text.lower() == "📅 расписание")
async def cmd_schedule(message: Message):
    schedule = load_json("data/schedule.json", get_default_schedule())
    text = "📅 Твой день:\n" + "\n".join([f"{item['time']} — {item['activity']}" for item in schedule])
    await message.answer(text)

@dp.message(F.text.lower() == "📝 чеклист")
async def cmd_checklist(message: Message):
    checklist = load_json("data/checklist.json", [])
    if not checklist:
        await message.answer("Чеклист пуст. Добавь задачи командой:\n<code>/добавить_задачу Погладить кота</code>")
        return
    text = "📋 Текущий чеклист:\n" + "\n".join([f"🔘 {item['task']}" for item in checklist])
    await message.answer(text)

@dp.message(Command("добавить_задачу"))
async def cmd_add_task(message: Message):
    text = message.text.replace("/добавить_задачу", "").strip()
    if not text:
        await message.answer("❗ После команды напиши текст задачи:\n<code>/добавить_задачу Выучить слова</code>")
        return
    checklist = load_json("data/checklist.json", [])
    checklist.append({"task": text, "date": datetime.now().strftime("%Y-%m-%d")})
    save_json("data/checklist.json", checklist)
    await message.answer("✅ Задача добавлена!")

@dp.message(F.text.lower() == "🎯 цели")
async def cmd_goals(message: Message):
    goals = load_json("data/goals.json", [])
    if not goals:
        await message.answer("Пока нет целей. Добавь командой:\n<code>/цель Стать лучшей версией себя</code>")
    else:
        text = "🎯 Твои цели:\n" + "\n".join([f"🔵 {goal}" for goal in goals])
        await message.answer(text)

@dp.message(Command("цель"))
async def cmd_add_goal(message: Message):
    text = message.text.replace("/цель", "").strip()
    if not text:
        await message.answer("❗ После команды напиши цель:\n<code>/цель Читать по 10 страниц</code>")
        return
    goals = load_json("data/goals.json", [])
    goals.append(text)
    save_json("data/goals.json", goals)
    await message.answer("🎯 Цель добавлена!")

@dp.message(F.text.lower() == "💬 цитата")
@dp.message(Command("цитата"))
async def cmd_quote(message: Message):
    quote = get_random_quote()
    await message.answer(f"💬 <i>{quote}</i>", parse_mode="HTML")

# ---------- MAIN ----------
async def main():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_quote, "cron", hour=6, minute=0, args=[bot, USER_ID])
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        print("[INFO] Бот запускается...")
        asyncio.run(main())
    except Exception as e:
        print("[ERROR] Ошибка при запуске:", e)
