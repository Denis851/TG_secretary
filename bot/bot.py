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
    [KeyboardButton(text="🧘 Отдых"), KeyboardButton(text="📊 Отчёт")]
], resize_keyboard=True)

mood_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="😊", callback_data="mood_happy"),
        InlineKeyboardButton(text="😐", callback_data="mood_neutral"),
        InlineKeyboardButton(text="😞", callback_data="mood_sad")
    ]
])

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

# --- Обработчики ---

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
    await message.answer("Закрой глаза, сделай глубокий вдох... 😌 4-7-8 дыхание")

@dp.message(F.text.lower() == "📊 отчёт")
async def cmd_report_button(message: Message):
    await cmd_report(message)

@dp.message(Command("настроение"))
async def cmd_mood(message: Message):
    await message.answer("Как ты себя чувствуешь?", reply_markup=mood_kb)

@dp.callback_query(F.data.startswith("mood_"))
async def handle_mood(callback: types.CallbackQuery):
    mood = callback.data.replace("mood_", "")
    mood_data = load_json("data/mood.json", [])
    mood_data.append({"time": datetime.now().isoformat(), "mood": mood})
    save_json("data/mood.json", mood_data)
    await callback.message.answer(f"Настроение зафиксировано: {mood}")
    await callback.answer()

@dp.message(Command("чеклист"))
async def cmd_checklist(message: Message):
    checklist = load_json("data/checklist.json", [])
    if not checklist:
        await message.answer("Чеклист пуст. Добавь задачи в файл checklist.json.")
        return
    text = "📝 Чеклист задач:\n" + "\n".join([f"- {item['task']}" for item in checklist])
    buttons = [
        [InlineKeyboardButton(text=f"✅ {item['task']}", callback_data=f"done_task_{i}")]
        for i, item in enumerate(checklist)
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer(text, reply_markup=markup)

@dp.callback_query(F.data.startswith("done_task_"))
async def handle_done_task(callback: types.CallbackQuery):
    index = int(callback.data.replace("done_task_", ""))
    checklist = load_json("data/checklist.json", [])
    if index < len(checklist):
        done_task = checklist.pop(index)
        save_json("data/checklist.json", checklist)
        await callback.message.edit_reply_markup()
        await callback.message.answer(f"🎉 Задача выполнена: <b>{done_task['task']}</b>")
    await callback.answer()

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
        return
    text = "🎯 Твои цели:\n" + "\n".join([f"- {g}" for g in goals])
    buttons = [
        [InlineKeyboardButton(text=f"✅ {g}", callback_data=f"done_goal_{i}")]
        for i, g in enumerate(goals)
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer(text, reply_markup=markup)

@dp.callback_query(F.data.startswith("done_goal_"))
async def handle_done_goal(callback: types.CallbackQuery):
    index = int(callback.data.replace("done_goal_", ""))
    goals = load_json("data/goals.json", [])
    if index < len(goals):
        done_goal = goals.pop(index)
        save_json("data/goals.json", goals)
        await callback.message.edit_reply_markup()
        await callback.message.answer(f"🏁 Цель выполнена: <b>{done_goal}</b>")
    await callback.answer()

@dp.message(Command("добавить_задачу"))
async def cmd_add_task(message: Message):
    text = message.text.replace("/добавить_задачу", "").strip()
    if not text:
        await message.answer("⚠️ Напиши задачу после команды, например: /добавить_задачу Помыть посуду")
        return
    checklist = load_json("data/checklist.json", [])
    checklist.append({"task": text, "date": datetime.today().strftime("%Y-%m-%d")})
    save_json("data/checklist.json", checklist)
    await message.answer("✅ Задача добавлена!")

@dp.message(Command("цитата"))
async def cmd_quote(message: Message):
    quote = get_random_quote()
    await message.answer(f"💬 {quote}")

@dp.message(Command("отчёт"))
async def cmd_report(message: Message):
    today = datetime.today().strftime("%Y-%m-%d")
    checklist = load_json("data/checklist.json", [])
    goals = load_json("data/goals.json", [])
    mood = load_json("data/mood.json", [])

    report = f"📝 Отчёт за {today}\n"
    report += "\n✅ Выполненные задачи:\n"
    for item in checklist:
        if item.get("date") == today:
            report += f" - {item.get('task', 'Без названия')}\n"
    report += "\n🎯 Цели:\n" + "\n".join([f" - {goal}" for goal in goals])
    today_mood = next((m['mood'] for m in reversed(mood) if today in m['time']), '—')
    report += f"\n😌 Настроение: {today_mood}\n"

    path = f"data/report_{today}.txt"
    with open(path, "w", encoding="utf-8") as f:
        f.write(report)
    await message.answer_document(document=FSInputFile(path), caption="📤 Твой отчёт готов!")

# --- Запуск ---

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
