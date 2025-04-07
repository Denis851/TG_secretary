import os
import json
import asyncio
from datetime import datetime
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart, Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from keyboards import main_kb, inline_actions_kb

# Загрузка переменных окружения
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
USER_ID = int(os.getenv("USER_ID", 0))

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Утилиты для работы с JSON

def load_json(path, default=[]):
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except:
        return default

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Хендлеры

@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer("Привет! 👋 Я твой ИИ-секретарь. Выбери действие:", reply_markup=main_kb)

@dp.message(F.text == "📅 Расписание")
async def schedule_handler(message: Message):
    await message.answer("🔔 Напоминания и расписание будут активированы по мере настройки...")

@dp.message(F.text == "🧠 Цели")
async def goals_handler(message: Message):
    goals = load_json("data/goals.json", [])
    if not goals:
        await message.answer("🎯 Целей пока нет. Добавь цель с помощью кнопки ниже:", reply_markup=inline_actions_kb)
    else:
        text = "🎯 Твои цели:\n" + "\n".join([f"- {g}" for g in goals])
        await message.answer(text, reply_markup=inline_actions_kb)

@dp.message(F.text == "✅ Чеклист")
async def checklist_handler(message: Message):
    tasks = load_json("data/checklist.json", [])
    if not tasks:
        await message.answer("📋 Чеклист пуст. Добавь задачу:", reply_markup=inline_actions_kb)
    else:
        text = "📋 Текущий чеклист:\n" + "\n".join([f"- {t['task']}" for t in tasks])
        await message.answer(text, reply_markup=inline_actions_kb)

@dp.message(F.text == "📊 Прогресс")
async def progress_handler(message: Message):
    await message.answer("📈 Визуализация прогресса в разработке. Следи за обновлениями!")

@dp.callback_query(F.data.in_(["done", "not_done", "add_task", "add_goal"]))
async def handle_action(callback: CallbackQuery):
    data = callback.data
    if data == "done":
        await callback.message.answer("✅ Отмечено как выполнено!")
    elif data == "not_done":
        await callback.message.answer("❌ Отмечено как не выполнено!")
    elif data == "add_task":
        await callback.message.answer("✍️ Введи новую задачу (чеклист):")
    elif data == "add_goal":
        await callback.message.answer("🎯 Напиши свою новую цель:")
    await callback.answer()

@dp.message(Command("отчёт"))
async def report_handler(message: Message):
    today = datetime.today().strftime("%Y-%m-%d")
    tasks = load_json("data/checklist.json", [])
    goals = load_json("data/goals.json", [])
    mood = load_json("data/mood.json", [])
    report = f"📝 Отчёт за {today}\n"
    report += "\n✅ Задачи:\n" + "\n".join([f"- {t['task']}" for t in tasks])
    report += "\n🎯 Цели:\n" + "\n".join([f"- {g}" for g in goals])
    today_mood = next((m['mood'] for m in reversed(mood) if today in m['time']), '—')
    report += f"\n\n😌 Настроение: {today_mood}\n"
    os.makedirs("data", exist_ok=True)
    path = f"data/report_{today}.txt"
    with open(path, 'w', encoding='utf-8') as f:
        f.write(report)
    await message.answer_document(FSInputFile(path), caption="📤 Вот твой отчёт")

# Запуск бота

async def main():
    scheduler = AsyncIOScheduler()
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print("[ERROR] Ошибка запуска:", e)
