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

# Inline-кнопки для задач (чеклиста)
def build_task_inline_kb(task_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Выполнено", callback_data=f"task_done:{task_id}"),
            InlineKeyboardButton(text="🚫 Не выполнено", callback_data=f"task_failed:{task_id}")
        ],
        [
            InlineKeyboardButton(text="✍️ Добавить задачу", callback_data="add_task")
        ]
    ])

# Inline-кнопки для целей
def build_goal_inline_kb(goal_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Выполнено", callback_data=f"goal_done:{goal_id}"),
            InlineKeyboardButton(text="🚫 Не выполнено", callback_data=f"goal_failed:{goal_id}")
        ],
        [
            InlineKeyboardButton(text="🎯 Добавить цель", callback_data="add_goal")
        ]
    ])

