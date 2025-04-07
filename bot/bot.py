import os
import json
import random
import asyncio
from datetime import datetime
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F, types
from aiogram.enums import ParseMode
from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from keyboards import main_menu_kb, checklist_inline_kb, goals_inline_kb

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
USER_ID = int(os.getenv("USER_ID", 0))

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# ====== Утилиты ======

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

def load_json(name, default=[]):
    path = os.path.join(DATA_DIR, name)
    if not os.path.exists(path): return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def save_json(name, data):
    path = os.path.join(DATA_DIR, name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_random_quote():
    quotes = load_json("quotes.txt", [])
    return random.choice(quotes) if quotes else "Каждый день — шанс начать заново."

# ====== Хендлеры ======

@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("👋 Привет! Я ИИ-секретарь. Что делаем?", reply_markup=main_menu_kb)

@dp.message(F.text == "Чеклист")
async def show_checklist(message: Message):
    checklist = load_json("checklist.json")
    if not checklist:
        await message.answer("📋 Чеклист пуст.")
    else:
        text = "📝 Твои задачи на день:\n" + "\n".join([f"- {item}" for item in checklist])
        await message.answer(text)
    await message.answer("Что сделать?", reply_markup=checklist_inline_kb)

@dp.message(F.text == "Цели")
async def show_goals(message: Message):
    goals = load_json("goals.json")
    if not goals:
        await message.answer("🎯 Целей пока нет.")
    else:
        text = "🎯 Твои цели:\n" + "\n".join([f"- {g}" for g in goals])
        await message.answer(text)
    await message.answer("Что сделать?", reply_markup=goals_inline_kb)

@dp.message(F.text == "Прогресс")
async def show_progress(message: Message):
    await message.answer("📈 Визуализация и аналитика в разработке.")

@dp.message(F.text == "Расписание")
async def show_schedule(message: Message):
    await message.answer("📅 Подключение редактора расписания скоро.")

@dp.callback_query(F.data == "add_task")
async def cb_add_task(callback: CallbackQuery):
    await callback.message.answer("✍️ Напиши задачу, которую нужно добавить в чеклист:")
    await callback.answer()
    dp.message.register(save_task_once)

async def save_task_once(message: Message):
    checklist = load_json("checklist.json")
    checklist.append(message.text)
    save_json("checklist.json", checklist)
    await message.answer("✅ Задача добавлена!", reply_markup=main_menu_kb)
    dp.message.unregister(save_task_once)

@dp.callback_query(F.data == "add_goal")
async def cb_add_goal(callback: CallbackQuery):
    await callback.message.answer("🎯 Напиши цель, которую нужно добавить:")
    await callback.answer()
    dp.message.register(save_goal_once)

async def save_goal_once(message: Message):
    goals = load_json("goals.json")
    goals.append(message.text)
    save_json("goals.json", goals)
    await message.answer("🎯 Цель добавлена!", reply_markup=main_menu_kb)
    dp.message.unregister(save_goal_once)

@dp.message(Command("отчёт"))
async def cmd_report(message: Message):
    today = datetime.today().strftime("%Y-%m-%d")
    checklist = load_json("checklist.json")
    goals = load_json("goals.json")
    report = f"📝 Отчёт за {today}\n\n✅ Задачи:\n" + "\n".join([f"- {t}" for t in checklist])
    report += "\n\n🎯 Цели:\n" + "\n".join([f"- {g}" for g in goals])

    path = f"{DATA_DIR}/report_{today}.txt"
    with open(path, "w", encoding="utf-8") as f:
        f.write(report)

    await message.answer_document(document=FSInputFile(path), caption="📤 Твой отчёт готов!")

# ====== Запуск ======

async def main():
    print("[INFO] Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
