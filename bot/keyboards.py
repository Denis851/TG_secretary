from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Главное меню (Reply Keyboard)
main_menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📅 Расписание")],
        [KeyboardButton(text="🎯 Цели")],
        [KeyboardButton(text="✅ Чеклист")],
        [KeyboardButton(text="📈 Прогресс")]
    ],
    resize_keyboard=True
)

# Inline-кнопки для чеклиста
checklist_inline_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="✅ Выполнено", callback_data="task_done"),
        InlineKeyboardButton(text="🚫 Не выполнено", callback_data="task_failed")
    ],
    [
        InlineKeyboardButton(text="✍️ Добавить задачу", callback_data="add_task")
    ]
])

# Inline-кнопки для целей
goals_inline_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="✅ Выполнено", callback_data="goal_done"),
        InlineKeyboardButton(text="🚫 Не выполнено", callback_data="goal_failed")
    ],
    [
        InlineKeyboardButton(text="🎯 Добавить цель", callback_data="add_goal")
    ]
])
