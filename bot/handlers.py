from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from keyboards import main_menu_kb, goals_inline_kb, checklist_inline_kb
from utils import load_json, get_random_quote
from fsm_states import FSMAddGoal, FSMAddTask
from aiogram.fsm.context import FSMContext

router = Router()

# /start — приветствие и главная клавиатура
@router.message(F.text == "/start")
async def cmd_start(message: Message):
    user_data = {"id": message.from_user.id}
    from utils import save_json
    save_json("data/user.json", user_data)

    await message.answer(
        "Привет! Я твой ИИ-секретарь 🤖. Чем займёмся сегодня?", 
        reply_markup=main_menu_kb
    )

# 💬 Цитата
@router.message(F.text == "💬 Цитата")
async def cmd_quote(message: Message):
    quote = get_random_quote()
    await message.answer(f"💬 {quote}")

# 📅 Расписание
@router.message(F.text == "📅 Расписание")
async def cmd_schedule(message: Message):
    schedule = load_json("data/schedule.json", [])
    if not schedule:
        await message.answer("📅 Расписание пусто.")
    else:
        text = "📆 Твоё расписание:\n\n" + "\n".join([f"{i+1}. {item}" for i, item in enumerate(schedule)])
        await message.answer(text)

# 🎯 Цели
@router.message(F.text == "🎯 Цели")
async def show_goals(message: Message, state: FSMContext):
    goals = load_json("data/goals.json", [])
    if not goals:
        await message.answer("🎯 Целей пока нет.", reply_markup=goals_inline_kb)
    else:
        for i, goal in enumerate(goals):
            status = "✅" if goal.get("done") else "❌"
            await message.answer(f"{status} {goal.get('text')}", reply_markup=goals_inline_kb)

# ✅ Чеклист
@router.message(F.text == "✅ Чеклист")
async def show_checklist(message: Message, state: FSMContext):
    tasks = load_json("data/checklist.json", [])
    if not tasks:
        await message.answer("📝 Чеклист пуст.", reply_markup=checklist_inline_kb)
    else:
        for i, task in enumerate(tasks):
            status = "✅" if task.get("done") else "❌"
            await message.answer(f"{status} {task.get('text')}", reply_markup=checklist_inline_kb)

# 📈 Прогресс
@router.message(F.text == "📈 Прогресс")
async def show_progress(message: Message):
    goals = load_json("data/goals.json", [])
    tasks = load_json("data/checklist.json", [])

    g_total = len(goals)
    g_done = len([g for g in goals if g.get("done")])
    t_total = len(tasks)
    t_done = len([t for t in tasks if t.get("done")])

    def bar(done, total):
        if total == 0:
            return "—"
        percent = int((done / total) * 10)
        return "▰" * percent + "▱" * (10 - percent)

    response = f"🎯 Цели: {g_done}/{g_total} {bar(g_done, g_total)}\n"
    response += f"📝 Задачи: {t_done}/{t_total} {bar(t_done, t_total)}"
    await message.answer(response)

# Обработка inline кнопок из checklist
@router.callback_query(F.data == "add_task")
async def add_task_prompt(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите новую задачу:")
    await state.set_state(FSMAddTask.text)
    await callback.answer()

@router.callback_query(F.data == "task_done")
async def task_done(callback: CallbackQuery):
    from utils import save_json
    tasks = load_json("data/checklist.json", [])
    if tasks:
        tasks[0]["done"] = True
        save_json("data/checklist.json", tasks)
        await callback.message.answer("✅ Задача отмечена как выполненная.")
    await callback.answer()

@router.callback_query(F.data == "task_fail")
async def task_fail(callback: CallbackQuery):
    from utils import save_json
    tasks = load_json("data/checklist.json", [])
    if tasks:
        tasks[0]["done"] = False
        save_json("data/checklist.json", tasks)
        await callback.message.answer("🚫 Задача отмечена как не выполненная.")
    await callback.answer()

# Обработка inline кнопок из goals
@router.callback_query(F.data == "add_goal")
async def add_goal_prompt(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите новую цель:")
    await state.set_state(FSMAddGoal.text)
    await callback.answer()

@router.callback_query(F.data == "goal_done")
async def goal_done(callback: CallbackQuery):
    from utils import save_json
    goals = load_json("data/goals.json", [])
    if goals:
        goals[0]["done"] = True
        save_json("data/goals.json", goals)
        await callback.message.answer("✅ Цель отмечена как выполненная.")
    await callback.answer()

@router.callback_query(F.data == "goal_fail")
async def goal_fail(callback: CallbackQuery):
    from utils import save_json
    goals = load_json("data/goals.json", [])
    if goals:
        goals[0]["done"] = False
        save_json("data/goals.json", goals)
        await callback.message.answer("🚫 Цель отмечена как не выполненная.")
    await callback.answer()

# Регистрация всех хендлеров
def register_handlers(dp):
    dp.include_router(router)
