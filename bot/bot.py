import os
import json
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, FSInputFile, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart, Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import matplotlib.pyplot as plt

# --- Загрузка .env ---
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
USER_ID = int(os.getenv("USER_ID"))

# --- Инициализация бота и диспетчера ---
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
scheduler = AsyncIOScheduler()

# --- Клавиатуры ---
main_kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [KeyboardButton(text="📅 Расписание"), KeyboardButton(text="🧠 Цели")],
    [KeyboardButton(text="✅ Чеклист"), KeyboardButton(text="📈 Прогресс")]
])

progress_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📤 Скачать график", callback_data="download_progress")]
])

# --- Вспомогательные функции ---
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

def generate_progress_chart():
    today = datetime.today().date()
    dates = [(today - timedelta(days=i)) for i in range(6, -1, -1)]
    progress = []
    for date in dates:
        date_str = date.isoformat()
        checklist = load_json("data/checklist.json", [])
        total = [i for i in checklist if i.get("date") == date_str]
        done = [i for i in total if i.get("done")]
        percent = int(len(done) / len(total) * 100) if total else 0
        progress.append(percent)

    plt.figure(figsize=(8, 4))
    plt.plot([d.strftime("%a") for d in dates], progress, marker="o")
    plt.title("Прогресс за неделю")
    plt.xlabel("День")
    plt.ylabel("% выполнения")
    plt.grid(True)
    path = "data/progress_chart.png"
    plt.savefig(path)
    plt.close()
    return path

# --- Обработчики ---
@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Привет, Ден! Я твой помощник по распорядку дня!", reply_markup=main_kb)

@dp.message(F.text == "📈 Прогресс")
async def show_progress(message: Message):
    path = generate_progress_chart()
    await message.answer_photo(FSInputFile(path), caption="Вот твой прогресс за последнюю неделю:", reply_markup=progress_kb)

@dp.callback_query(F.data == "download_progress")
async def send_chart(callback: types.CallbackQuery):
    await callback.message.answer_document(FSInputFile("data/progress_chart.png"), caption="📊 Твой прогресс")
    await callback.answer()

# --- Запуск ---
async def main():
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        print("[INFO] Бот запускается...")
        asyncio.run(main())
    except Exception as e:
        print("[ERROR] Ошибка:", e)
