from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.markdown import hbold
from aiogram import F
from aiogram.filters import CommandStart
import asyncio
import json
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from keyboards import main_menu_kb, build_task_inline_kb, build_goal_inline_kb

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler()

DATA_PATH = "data"
CHECKLIST_FILE = os.path.join(DATA_PATH, "checklist.json")
GOALS_FILE = os.path.join(DATA_PATH, "goals.json")


def load_json(path, default=None):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default if default is not None else []


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def progress_bar(completed, total):
    percent = int((completed / total) * 10) if total else 0
    return "▮" * percent + "▯" * (10 - percent) + f" {completed}/{total}"


@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Привет, Ден! Я твой помощник по распорядку дня!", reply_markup=main_menu_kb)


@dp.message(F.text == "📅 Расписание")
async def show_schedule(message: Message):
    await message.answer("Расписание пока не добавлено.")


@dp.message(F.text == "🎯 Цели")
async def show_goals(message: Message):
    goals = load_json(GOALS_FILE)
    if not goals:
        await message.answer("Цели пока не добавлены.")
    else:
        for idx, goal in enumerate(goals):
            text = f"🎯 {goal['text']} {'✅' if goal.get('done') else '❌'}"
            await message.answer(text, reply_markup=build_goal_inline_kb(idx))
        await message.answer("🎯 Добавить цель:", reply_markup=build_goal_inline_kb("add"))


@dp.message(F.text == "✅ Чеклист")
async def show_checklist(message: Message):
    tasks = load_json(CHECKLIST_FILE)
    if not tasks:
        await message.answer("Задачи пока не добавлены.")
    else:
        for idx, task in enumerate(tasks):
            text = f"☑️ {task['text']} {'✅' if task.get('done') else '❌'}"
            await message.answer(text, reply_markup=build_task_inline_kb(idx))
        await message.answer("✍️ Добавить задачу:", reply_markup=build_task_inline_kb("add"))


@dp.message(F.text == "📈 Прогресс")
async def show_progress(message: Message):
    tasks = load_json(CHECKLIST_FILE)
    goals = load_json(GOALS_FILE)
    all_items = tasks + goals
    done = sum(1 for item in all_items if item.get("done"))
    total = len(all_items)
    bar = progress_bar(done, total)
    await message.answer(f"📊 Общий прогресс:\n{bar}")


@dp.callback_query(F.data.startswith("add_task"))
async def ask_new_task(callback: CallbackQuery):
    await callback.message.answer("Напиши задачу, которую хочешь добавить:")
    await callback.answer()
    dp.message.register(handle_new_task, F.text)


async def handle_new_task(message: Message):
    tasks = load_json(CHECKLIST_FILE)
    tasks.append({"text": message.text, "done": False})
    save_json(CHECKLIST_FILE, tasks)
    await message.answer("Задача добавлена ✅")
    dp.message.unregister(handle_new_task)


@dp.callback_query(F.data.startswith("add_goal"))
async def ask_new_goal(callback: CallbackQuery):
    await callback.message.answer("Напиши цель, которую хочешь добавить:")
    await callback.answer()
    dp.message.register(handle_new_goal, F.text)


async def handle_new_goal(message: Message):
    goals = load_json(GOALS_FILE)
    goals.append({"text": message.text, "done": False})
    save_json(GOALS_FILE, goals)
    await message.answer("Цель добавлена ✅")
    dp.message.unregister(handle_new_goal)


@dp.callback_query(F.data.startswith("task_done"))
async def mark_task_done(callback: CallbackQuery):
    idx = int(callback.data.split(":")[1])
    tasks = load_json(CHECKLIST_FILE)
    if 0 <= idx < len(tasks):
        tasks[idx]["done"] = True
        save_json(CHECKLIST_FILE, tasks)
        await callback.message.edit_text(f"☑️ {tasks[idx]['text']} ✅")
    await callback.answer("Задача отмечена как выполнена!")


@dp.callback_query(F.data.startswith("task_failed"))
async def mark_task_failed(callback: CallbackQuery):
    idx = int(callback.data.split(":")[1])
    tasks = load_json(CHECKLIST_FILE)
    if 0 <= idx < len(tasks):
        tasks[idx]["done"] = False
        save_json(CHECKLIST_FILE, tasks)
        await callback.message.edit_text(f"☑️ {tasks[idx]['text']} ❌")
    await callback.answer("Задача отмечена как невыполненная.")


@dp.callback_query(F.data.startswith("goal_done"))
async def mark_goal_done(callback: CallbackQuery):
    idx = int(callback.data.split(":")[1])
    goals = load_json(GOALS_FILE)
    if 0 <= idx < len(goals):
        goals[idx]["done"] = True
        save_json(GOALS_FILE, goals)
        await callback.message.edit_text(f"🎯 {goals[idx]['text']} ✅")
    await callback.answer("Цель выполнена!")


@dp.callback_query(F.data.startswith("goal_failed"))
async def mark_goal_failed(callback: CallbackQuery):
    idx = int(callback.data.split(":")[1])
    goals = load_json(GOALS_FILE)
    if 0 <= idx < len(goals):
        goals[idx]["done"] = False
        save_json(GOALS_FILE, goals)
        await callback.message.edit_text(f"🎯 {goals[idx]['text']} ❌")
    await callback.answer("Цель помечена как не выполнена.")


async def main():
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())