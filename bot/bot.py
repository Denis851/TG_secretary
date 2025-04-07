# Шаг 1: Добавим инлайн-кнопки для "Выполнено" в чеклист и цели

from aiogram.utils.keyboard import InlineKeyboardBuilder

# Обновим cmd_checklist и cmd_goals:

@dp.message(F.text.lower() == "📋 чеклист")
async def cmd_checklist(message: Message):
    checklist = load_json("data/checklist.json", [])
    if not checklist:
        await message.answer("Чеклист пуст. Добавь задачи командой:\n<code>/добавить_задачу Сделать зарядку</code>")
        return

    for idx, item in enumerate(checklist):
        status = "✅" if item.get("done") else "🔘"
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
            text="✅ Выполнено" if not item.get("done") else "❌ Не выполнено",
            callback_data=f"check_{idx}"
        )]])
        await message.answer(f"{status} {item['task']}", reply_markup=kb)

@dp.callback_query(F.data.startswith("check_"))
async def mark_checklist_done(callback: types.CallbackQuery):
    idx = int(callback.data.split("_")[1])
    checklist = load_json("data/checklist.json", [])
    if 0 <= idx < len(checklist):
        checklist[idx]["done"] = not checklist[idx].get("done", False)
        save_json("data/checklist.json", checklist)
        await callback.answer("Обновлено!")
        await cmd_checklist(callback.message)


@dp.message(F.text.lower() == "🌟 цели")
async def cmd_goals(message: Message):
    goals = load_json("data/goals.json", [])
    if not goals:
        await message.answer("Целей нет. Добавь командой:\n<code>/цель Прочитать книгу</code>")
        return
    for idx, goal in enumerate(goals):
        if isinstance(goal, dict):
            text = goal.get("text", "—")
            done = goal.get("done", False)
        else:
            text = goal
            done = False
            goals[idx] = {"text": goal, "done": False}

        status = "✅" if done else "🔘"
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
            text="✅ Выполнено" if not done else "❌ Не выполнено",
            callback_data=f"goal_{idx}"
        )]])
        await message.answer(f"{status} {text}", reply_markup=kb)
    save_json("data/goals.json", goals)

@dp.callback_query(F.data.startswith("goal_"))
async def mark_goal_done(callback: types.CallbackQuery):
    idx = int(callback.data.split("_")[1])
    goals = load_json("data/goals.json", [])
    if 0 <= idx < len(goals):
        goals[idx]["done"] = not goals[idx].get("done", False)
        save_json("data/goals.json", goals)
        await callback.answer("Обновлено!")
        await cmd_goals(callback.message)
