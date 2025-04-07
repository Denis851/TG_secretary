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

from bot.analyze import daily_report

# Загрузка .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
USER_ID = int(os.getenv("USER_ID"))

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

main_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="🌅 Утро"), KeyboardButton(text="💻 Продуктивность")],
    [KeyboardButton(text="🧘 Отдых"), KeyboardButton(text="📊 Отчёт")]
], resize_keyboard=True)

mood_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="😊", callback_data="mood_happy"),
     InlineKeyboardButton(text="😐", callback_data="mood_neutral"),
     InlineKeyboardButton(text="😞", callback_data="mood_sad")]
])

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
    await bot.send_message(user_id, f"💬 Цитата дня:\n{quote}")

@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Привет, Ден! Я твой ИИ-секретарь, готов к работе!", reply_markup=main_kb)

@dp.message(F.text.lower() == "🌅 утро")
async def morning(message: Message):
    await message.answer("Доброе утро! Вот твои команды:", reply_markup=main_kb)
    await cmd_checklist(message)

@dp.message(F.text.lower() == "💻 продуктивность")
async def productivity(message: Message):
    await message.answer("🧠 Время фокуса! Запускаю фокус-сессию на 45 минут.")

@dp.message(F.text.lower() == "🧘 отдых")
async def relax(message: Message):
    await message.answer("Закрой глаза, сделай глубокий вдох... 😌")

@dp.message(F.text.lower() == "📊 отчёт")
async def cmd_report_button(message: Message):
    await cmd_report(message)

@dp.message(Command("цитата"))
async def cmd_quote(message: Message):
    quote = get_random_quote()
    await message.answer(f"💬 {quote}")

@dp.message(Command("цель"))
async def cmd_add_goal(message: Message):
    text = message.text.replace("/цель", "").strip()
    if not text:
        await message.answer("Напиши цель после команды /цель [текст цели]")
        return
    goals = load_json("data/goals.json", [])
    goals.append(text)
    save_json("data/goals.json", goals)
    await message.answer("🎯 Цель добавлена!")

@dp.message(Command("цели"))
async def cmd_goals(message: Message):
    goals = load_json("data/goals.json", [])
    if not goals:
        await message.answer("Целей пока нет.")
    else:
        text = "🎯 Твои цели:" + "".join([f"- {g}" for g in goals])
        await message.answer(text)

@dp.message(Command("добавить_задачу"))
async def cmd_add_task(message: Message):
    text = message.text.replace("/добавить_задачу", "").strip()
    if not text:
        await message.answer("⚠️ Напиши задачу после команды, например: /добавить_задачу Помыть посуду")
        return
    checklist = load_json("data/checklist.json", [])
    checklist.append({"task": text, "date": datetime.today().strftime("%Y-%m-%d")})
    save_json("data/checklist.json", checklist)
    await message.answer("🆕 Задача добавлена!")

@dp.message(Command("чеклист"))
async def cmd_checklist(message: Message):
    checklist = load_json("data/checklist.json", [])
    if not checklist:
        await message.answer("Чеклист пуст. Добавь задачи в файл checklist.json.")
        return
    text = "📝 Чеклист задач:
" + "
".join([f"- {item['task']}" for item in checklist])
    await message.answer(text)

@dp.message(Command("отчёт"))
async def cmd_report(message: Message):
    today = datetime.today().strftime("%Y-%m-%d")
    checklist = load_json("data/checklist.json", [])
    goals = load_json("data/goals.json", [])
    mood = load_json("data/mood.json", [])

    report = f"📝 Отчёт за {today}
"
    report += "
✅ Выполненные задачи:
"
    for item in checklist:
        if item.get("date") == today:
            report += f" - {item.get('task', 'Без названия')}
"
    report += "
🎯 Цели:
" + "
".join([f" - {goal}" for goal in goals])
    today_mood = next((m['mood'] for m in reversed(mood) if today in m['time']), '—')
    report += f"
😌 Настроение: {today_mood}
"

    path = f"data/report_{today}.txt"
    with open(path, "w", encoding="utf-8") as f:
        f.write(report)
    await message.answer_document(document=FSInputFile(path), caption="📤 Твой отчёт готов!")

async def main():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(daily_report, 'cron', hour=21, minute=0, args=[bot, USER_ID])
    scheduler.add_job(send_quote, 'cron', hour=6, minute=0, args=[bot, USER_ID])
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        print("[INFO] Бот запускается...")
        asyncio.run(main())
    except Exception as e:
        print("[ERROR] Ошибка при запуске:", e)
