import os
import json
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Загрузка переменных окружения
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
USER_ID = int(os.getenv("USER_ID", "0"))
if not BOT_TOKEN or USER_ID == 0:
    raise ValueError("Не задан BOT_TOKEN или USER_ID!")


# Инициализация бота
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
scheduler = AsyncIOScheduler()

# --- Клавиатуры ---
def get_main_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📅 Расписание"), KeyboardButton(text="🧠 Цели")],
        [KeyboardButton(text="✅ Чеклист"), KeyboardButton(text="📊 Прогресс")]
    ], resize_keyboard=True)

def load_json(path, default=[]):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def progress_bar(completed, total):
    percent = int((completed / total) * 10) if total else 0
    return "▰" * percent + "▱" * (10 - percent) + f" {completed}/{total}"

@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Привет, Ден! Я твой помощник по распорядку дня!", reply_markup=main_kb)

@dp.message(F.text.lower() == "📅 расписание")
async def show_schedule(message: Message):
    schedule = load_json("data/schedule.json")
    if not schedule:
async def cmd_start(message: Message):
    await message.answer("Нет расписания")


@dp.message(F.text.lower() == "🧠 цели")
async def show_goals(message: Message):
    goals = load_json("data/goals.json")
    if not goals:
        await message.answer("Целей пока нет. Добавь через кнопку.")
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Выполнено", callback_data=f"goal_done:{i}")]
        for i, g in enumerate(goals)
    ] + [[InlineKeyboardButton(text="➕ Добавить цель", callback_data="add_goal")]])



@dp.message(F.text.lower() == "✅ чеклист")
async def show_checklist(message: Message):
    tasks = load_json("data/checklist.json")
    if not tasks:
        await message.answer("Чеклист пуст. Добавь задачу через кнопку.")
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Выполнено", callback_data=f"task_done:{i}")]
        for i, t in enumerate(tasks)
    ] + [[InlineKeyboardButton(text="➕ Добавить задачу", callback_data="add_task")]])


@dp.message(F.text.lower() == "📊 прогресс")
async def show_progress(message: Message):
    tasks = load_json("data/checklist.json")
    goals = load_json("data/goals.json")
    done_tasks = len([t for t in tasks if str(t).startswith("✅")])
    done_goals = len([g for g in goals if str(g).startswith("✅")])
    task_bar = progress_bar(done_tasks, len(tasks))
	await message.answer(f"📊 Прогресс целей:{goal_bar}")

@dp.callback_query(F.data.startswith("task_done:"))
async def mark_task_done(callback: CallbackQuery):
    tasks = load_json("data/checklist.json")
    index = int(callback.data.split(":")[1])
    if index < len(tasks):
        tasks[index] = f"✅ {tasks[index]}"
        save_json("data/checklist.json", tasks)
        await callback.answer("Задача выполнена!")
        await callback.message.delete()
        await show_checklist(callback.message)

@dp.callback_query(F.data.startswith("goal_done:"))
async def mark_goal_done(callback: CallbackQuery):
    goals = load_json("data/goals.json")
    index = int(callback.data.split(":")[1])
    if index < len(goals):
        goals[index] = f"✅ {goals[index]}"
        save_json("data/goals.json", goals)
        await callback.answer("Цель выполнена!")
        await callback.message.delete()
        await show_goals(callback.message)

@dp.callback_query(F.data == "add_task")
async def ask_new_task(callback: CallbackQuery):
    await callback.message.answer("Напиши новую задачу:")
    dp.message.register(handle_new_task)

async def handle_new_task(message: Message):
    task = message.text.strip()
    tasks = load_json("data/checklist.json")
    tasks.append(task)
    save_json("data/checklist.json", tasks)
    await message.answer("Задача добавлена ✅", reply_markup=main_kb)

@dp.callback_query(F.data == "add_goal")
async def ask_new_goal(callback: CallbackQuery):
    await callback.message.answer("Напиши новую цель:")
    dp.message.register(handle_new_goal)

async def handle_new_goal(message: Message):
    goal = message.text.strip()
    goals = load_json("data/goals.json")
    goals.append(goal)
    save_json("data/goals.json", goals)
    await message.answer("Цель добавлена ✅", reply_markup=main_kb)

async def send_daily_reminder():
    await bot.send_message(USER_ID, "🔔 Напоминание: проверь расписание и цели на день!", reply_markup=main_kb)

# Главный запуск
async def main():
    scheduler.add_job(send_daily_reminder, "cron", hour=6, minute=0)
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())


